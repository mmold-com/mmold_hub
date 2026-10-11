"""Create the first ERPNext site from mounted secret files.

This is deliberately an explicit, one-shot Compose profile. It refuses to
overwrite an existing site and keeps passwords out of command-line arguments
and Compose environment output.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


def read_secret(path: str) -> str:
    value = Path(path).read_text(encoding="utf-8").rstrip("\r\n")
    if not value:
        raise SystemExit(f"Required secret file is empty: {path}")
    return value


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: bootstrap_site.py <site-name>")

    site = sys.argv[1]
    if not re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9.-]*[A-Za-z0-9])?", site):
        raise SystemExit("Site name contains unsupported characters")

    site_config = Path("sites", site, "site_config.json")
    if site_config.exists() or site_config.parent.exists():
        raise SystemExit(f"Site path already exists; refusing to overwrite: {site}")

    db_root_password = read_secret("/run/secrets/db_root_password")
    admin_password = read_secret("/run/secrets/erp_admin_password")

    import frappe
    from frappe.installer import _new_site

    # The bench image runs with the bench root as its working directory, but
    # Frappe's shared app manifest lives under ``sites/apps.txt``.  Pass the
    # mounted sites directory explicitly; otherwise init searches ``./apps.txt``
    # and aborts before _new_site can create the site directories.
    frappe.init(site, sites_path="sites", new_site=True)
    _new_site(
        db_name=None,
        site=site,
        db_root_username="root",
        db_root_password=db_root_password,
        admin_password=admin_password,
        install_apps=["erpnext", "mmold_hub", "print_designer"],
        mariadb_user_host_login_scope="%",
    )
    print(f"Site {site} was created with ERPNext, MMold Hub and Print Designer.")


if __name__ == "__main__":
    main()
