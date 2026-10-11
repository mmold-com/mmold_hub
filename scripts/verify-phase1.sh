#!/usr/bin/env bash
set -euo pipefail

check() {
  local path="$1" expected_tag="$2" expected_commit="$3"
  test "$(git -C "$path" rev-parse HEAD)" = "$expected_commit"
  test "$(git -C "$path" describe --tags --exact-match HEAD)" = "$expected_tag"
  test -z "$(git -C "$path" status --porcelain)"
  git -C "$path" fsck --no-dangling
}

check upstream/frappe-v16.36.0 v16.36.0 f3f0c0b13c77a419487150a198fed42964e1919e
check upstream/erpnext-v16.37.0 v16.37.0 af63cde4941570ec7b9e12422c68302762cfcf91
check upstream/frappe_docker v3.2.2 3061850feface8fbbad15b5dc08a110c596107cb
check reference_apps/print_designer v1.6.7 d0d9bb9961c588c19d4201f9419737b67973a90a
check reference_apps/pdf_on_submit v16.3.0 c62360be7a3719074b5defa3279ca332c4b8d9f3
check services/mcp-erpnext v3.0.4 cca6e96da4c3f66cb5a0e312129a142e465d1109

echo "Phase 1 source verification passed."
