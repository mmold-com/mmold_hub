#!/usr/bin/env bash
set -euo pipefail

PYTHONPATH=. python3 -m unittest discover -s mmold_hub/tests -v
python3 -m compileall -q mmold_hub
python3 -c 'import pathlib, tomllib; data = tomllib.loads(pathlib.Path("pyproject.toml").read_text()); assert data["project"]["name"] == "mmold_hub"'

for path in \
	upstream/frappe-v16.36.0 \
	upstream/erpnext-v16.37.0 \
	upstream/frappe \
	upstream/erpnext \
	reference_apps/print_designer \
	reference_apps/pdf_on_submit; do
	status="$(git -C "$path" status --porcelain)"
	test -z "$status"
done

git diff --check
echo "Phase 2 static verification passed."
