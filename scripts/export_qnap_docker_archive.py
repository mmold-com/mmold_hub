#!/usr/bin/env python3
"""Convert a single-platform OCI image-layout tar into a Docker archive tar.

This is intended for older Docker-compatible importers that require a root
manifest.json (for example, legacy Container Station versions). It does not
run containers or contact a registry.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import tarfile
import tempfile
from pathlib import PurePosixPath


def read_json(archive: tarfile.TarFile, name: str) -> dict:
    member = archive.getmember(name)
    stream = archive.extractfile(member)
    if stream is None:
        raise ValueError(f"missing archive member: {name}")
    return json.load(stream)


def blob_member(digest: str) -> str:
    algorithm, value = digest.split(":", 1)
    if algorithm != "sha256" or len(value) != 64:
        raise ValueError(f"unsupported digest: {digest}")
    return f"blobs/sha256/{value}"


def add_bytes(output: tarfile.TarFile, name: str, value: bytes) -> None:
    info = tarfile.TarInfo(name)
    info.size = len(value)
    info.mode = 0o644
    output.addfile(info, io.BytesIO(value))


def chain_id(parent: str | None, diff_id: str) -> str:
    if parent is None:
        return diff_id.removeprefix("sha256:")
    value = hashlib.sha256(f"{parent} {diff_id}".encode()).hexdigest()
    return value


def convert(source: str, destination: str, tag: str, platform: str) -> None:
    os_name, arch = platform.split("/", 1)
    with tarfile.open(source, "r:*") as image:
        layout = read_json(image, "index.json")
        candidates = []
        for descriptor in layout.get("manifests", []):
            manifest_path = blob_member(descriptor["digest"])
            manifest = read_json(image, manifest_path)
            if manifest.get("mediaType") == "application/vnd.oci.image.index.v1+json":
                for child in manifest.get("manifests", []):
                    child_platform = child.get("platform", {})
                    if (child_platform.get("os"), child_platform.get("architecture")) == (os_name, arch):
                        candidates.append(read_json(image, blob_member(child["digest"])))
            elif descriptor.get("platform", {}).get("os") == os_name and descriptor.get("platform", {}).get("architecture") == arch:
                candidates.append(manifest)

        if len(candidates) != 1:
            raise ValueError(f"expected one {platform} image manifest; found {len(candidates)}")
        manifest = candidates[0]
        config_descriptor = manifest["config"]
        config_stream = image.extractfile(blob_member(config_descriptor["digest"]))
        if config_stream is None:
            raise ValueError("missing image config blob")
        config_bytes = config_stream.read()
        if hashlib.sha256(config_bytes).hexdigest() != config_descriptor["digest"].split(":", 1)[1]:
            raise ValueError("image config digest mismatch")
        config = json.loads(config_bytes)
        if (config.get("os"), config.get("architecture")) != (os_name, arch):
            raise ValueError("OCI config platform does not match the requested platform")

        layers = manifest["layers"]
        diff_ids = config.get("rootfs", {}).get("diff_ids", [])
        if len(layers) != len(diff_ids):
            raise ValueError("OCI layer count does not match config rootfs.diff_ids")

        config_name = config_descriptor["digest"].split(":", 1)[1] + ".json"
        docker_layers = []
        chain_ids = []
        parent = None
        for diff_id in diff_ids:
            parent = chain_id(parent, diff_id)
            chain_ids.append(parent)
            docker_layers.append(f"{parent}/layer.tar")

        docker_manifest = [{"Config": config_name, "RepoTags": [tag], "Layers": docker_layers}]
        repositories = {tag.rsplit(":", 1)[0]: {tag.rsplit(":", 1)[1]: chain_ids[-1]}}

        with tarfile.open(destination, "w", format=tarfile.PAX_FORMAT) as output:
            add_bytes(output, "manifest.json", json.dumps(docker_manifest, separators=(",", ":")).encode())
            add_bytes(output, config_name, config_bytes)
            add_bytes(output, "repositories", json.dumps(repositories, separators=(",", ":")).encode())
            parent_id = None
            for layer, layer_path, layer_id, diff_id in zip(layers, docker_layers, chain_ids, diff_ids, strict=True):
                layer_dir = str(PurePosixPath(layer_path).parent)
                add_bytes(output, f"{layer_dir}/VERSION", b"1.0\n")
                legacy = {"id": layer_id}
                if parent_id:
                    legacy["parent"] = parent_id
                add_bytes(output, f"{layer_dir}/json", json.dumps(legacy, separators=(",", ":")).encode())
                compressed = image.extractfile(blob_member(layer["digest"]))
                if compressed is None:
                    raise ValueError(f"missing layer blob: {layer['digest']}")
                if layer.get("mediaType") != "application/vnd.oci.image.layer.v1.tar+gzip":
                    raise ValueError(f"unsupported layer media type: {layer.get('mediaType')}")
                with gzip.GzipFile(fileobj=compressed, mode="rb") as uncompressed:
                    info = tarfile.TarInfo(layer_path)
                    # OCI compressed sizes differ from uncompressed sizes. Stream the layer to a
                    # seekable temporary file so the exact uncompressed tar size can be recorded.
                    with tempfile.TemporaryFile() as layer_file:
                        digest = hashlib.sha256()
                        while chunk := uncompressed.read(1024 * 1024):
                            digest.update(chunk)
                            layer_file.write(chunk)
                        expected = diff_id.split(":", 1)[1]
                        if digest.hexdigest() != expected:
                            raise ValueError(f"uncompressed layer digest mismatch: {layer['digest']}")
                        info.size = layer_file.tell()
                        info.mode = 0o644
                        layer_file.seek(0)
                        output.addfile(info, layer_file)
                parent_id = layer_id


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", help="OCI layout archive (.tar)")
    parser.add_argument("destination", help="Docker archive output (.tar)")
    parser.add_argument("--tag", required=True, help="single image tag to include")
    parser.add_argument("--platform", default="linux/amd64")
    args = parser.parse_args()
    convert(args.source, args.destination, args.tag, args.platform)


if __name__ == "__main__":
    main()
