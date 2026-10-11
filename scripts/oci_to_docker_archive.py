#!/usr/bin/env python3
"""Convert an OCI image archive with Docker-compatible manifest.json to a legacy Docker archive.

This is useful for older Container Station importers that reject OCI layer-blob paths.
The converter verifies every unpacked layer against the image config's rootfs.diff_ids.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import os
import tarfile
import tempfile
from pathlib import Path


def _add_bytes(archive: tarfile.TarFile, name: str, data: bytes) -> None:
    info = tarfile.TarInfo(name)
    info.size = len(data)
    info.mode = 0o644
    archive.addfile(info, io.BytesIO(data))


def convert(source: Path, destination: Path) -> None:
    with tarfile.open(source, "r:*") as src:
        manifest = json.load(src.extractfile("manifest.json"))
        if len(manifest) != 1:
            raise ValueError("Expected exactly one image in the source archive")
        image = manifest[0]
        config_bytes = src.extractfile(image["Config"]).read()
        config = json.loads(config_bytes)
        diff_ids = config["rootfs"]["diff_ids"]
        layers = image["Layers"]
        if len(diff_ids) != len(layers):
            raise ValueError("Layer count does not match config rootfs.diff_ids")

        docker_manifest = [{
            "Config": Path(image["Config"]).name,
            "RepoTags": image.get("RepoTags", []),
            "Layers": [],
        }]
        chain_id = None
        with tarfile.open(destination, "w", format=tarfile.PAX_FORMAT) as out:
            _add_bytes(out, docker_manifest[0]["Config"], config_bytes)
            for layer_name, diff_id in zip(layers, diff_ids, strict=True):
                chain_id = diff_id if chain_id is None else "sha256:" + hashlib.sha256(
                    (chain_id + " " + diff_id).encode("ascii")
                ).hexdigest()
                docker_layer = f"{chain_id.removeprefix('sha256:')}/layer.tar"
                docker_manifest[0]["Layers"].append(docker_layer)
                source_layer = src.extractfile(layer_name)
                digest = hashlib.sha256()
                with tempfile.TemporaryFile() as unpacked:
                    with gzip.GzipFile(fileobj=source_layer, mode="rb") as gz:
                        while chunk := gz.read(1024 * 1024):
                            digest.update(chunk)
                            unpacked.write(chunk)
                    if "sha256:" + digest.hexdigest() != diff_id:
                        raise ValueError(f"Unpacked layer digest mismatch: {layer_name}")
                    size = unpacked.tell()
                    unpacked.seek(0)
                    info = tarfile.TarInfo(docker_layer)
                    info.size = size
                    info.mode = 0o644
                    out.addfile(info, unpacked)

            _add_bytes(out, "manifest.json", json.dumps(docker_manifest, separators=(",", ":")).encode())

    os.chmod(destination, 0o600)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    convert(args.source, args.destination)
    print(f"Created Docker archive: {args.destination}")


if __name__ == "__main__":
    main()
