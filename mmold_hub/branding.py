"""Reversible, conservative Site-level MMold Hub brand defaults."""

from __future__ import annotations

import json

SNAPSHOT_KEY = "mmold_hub.branding.snapshot.v1"
LOGO = "/assets/mmold_hub/images/mmold-hub-logo.png"

MANAGED_VALUES = {
	"Website Settings": {"app_name": "MMold Hub", "app_logo": LOGO},
	"Navbar Settings": {"app_logo": LOGO},
}

SUPPORT_ITEM_LABEL = "MMold Hub Support"
SUPPORT_ITEM_ROUTE = "https://mmold.com"

UPSTREAM_DEFAULTS = {
	"app_name": {"", "Frappe", "ERPNext", "Frappe Framework"},
	"app_logo": {
		"",
		"/assets/frappe/images/frappe-framework-logo.svg",
		"/assets/frappe/images/frappe-logo.png",
		"/assets/erpnext/images/erpnext-logo.svg",
		"/assets/erpnext/images/erpnext-logo.png",
	},
}


def apply_branding_defaults() -> dict:
	"""Apply defaults only over known upstream values and keep a restore snapshot."""
	import frappe

	raw_snapshot = frappe.defaults.get_global_default(SNAPSHOT_KEY)
	snapshot = json.loads(raw_snapshot) if raw_snapshot else {}
	# Discard keys from earlier MMold Hub builds that were not real DocType fields.
	for doctype in list(snapshot):
		valid = set(MANAGED_VALUES.get(doctype, {})) | {"support_item"}
		snapshot[doctype] = {key: value for key, value in snapshot[doctype].items() if key in valid}
		if not snapshot[doctype]:
			del snapshot[doctype]
	skipped = []
	for doctype, values in MANAGED_VALUES.items():
		doc = frappe.get_single(doctype)
		changed = False
		for fieldname, managed_value in values.items():
			current = doc.get(fieldname) or ""
			if current == managed_value:
				continue
			if current not in UPSTREAM_DEFAULTS[fieldname]:
				skipped.append(f"{doctype}.{fieldname}")
				continue
			if fieldname not in snapshot.get(doctype, {}):
				snapshot.setdefault(doctype, {})[fieldname] = doc.get(fieldname)
			doc.set(fieldname, managed_value)
			changed = True
		if changed:
			doc.save(ignore_permissions=True)

	navbar = frappe.get_single("Navbar Settings")
	support_item = next((item for item in navbar.help_dropdown if item.item_label == "Frappe Support"), None)
	if support_item:
		if support_item.route == SUPPORT_ITEM_ROUTE and support_item.item_label == SUPPORT_ITEM_LABEL:
			pass
		elif support_item.route == "https://frappe.io/support" and support_item.item_label == "Frappe Support":
			snapshot.setdefault("Navbar Settings", {}).setdefault("support_item", {
				"name": support_item.name,
				"item_label": support_item.item_label,
				"route": support_item.route,
			})
			support_item.item_label = SUPPORT_ITEM_LABEL
			support_item.route = SUPPORT_ITEM_ROUTE
			navbar.save(ignore_permissions=True)
		else:
			skipped.append("Navbar Settings.help_dropdown.Frappe Support")

	frappe.defaults.set_global_default(SNAPSHOT_KEY, json.dumps(snapshot, ensure_ascii=False))
	frappe.clear_cache()
	return {"status": "applied", "snapshot": snapshot, "skipped": skipped}


def restore_branding_defaults() -> dict:
	"""Restore saved Site values, but never overwrite a later administrator edit."""
	import frappe

	raw_snapshot = frappe.defaults.get_global_default(SNAPSHOT_KEY)
	if not raw_snapshot:
		return {"status": "not_managed", "restored": []}

	snapshot = json.loads(raw_snapshot)
	restored = []
	for doctype, fields in snapshot.items():
		doc = frappe.get_single(doctype)
		changed = False
		for fieldname, original_value in fields.items():
			if fieldname == "support_item":
				item = next((row for row in doc.help_dropdown if row.name == original_value.get("name")), None)
				# Frappe may recreate standard child rows with a new name during sync.
				if not item:
					item = next(
						(row for row in doc.help_dropdown
						 if row.item_label == SUPPORT_ITEM_LABEL and row.route == SUPPORT_ITEM_ROUTE),
						None,
					)
				if item and item.item_label == SUPPORT_ITEM_LABEL and item.route == SUPPORT_ITEM_ROUTE:
					item.item_label = original_value["item_label"]
					item.route = original_value["route"]
					changed = True
					restored.append(f"Navbar Settings.help_dropdown.{original_value['name']}")
				continue
			if doc.get(fieldname) == MANAGED_VALUES[doctype][fieldname]:
				doc.set(fieldname, original_value)
				restored.append(f"{doctype}.{fieldname}")
				changed = True
		if changed:
			doc.save(ignore_permissions=True)

	frappe.defaults.clear_default(SNAPSHOT_KEY)
	frappe.clear_cache()
	return {"status": "restored", "restored": restored}


def get_branding_status() -> dict:
	"""Return runtime brand settings for isolated-site acceptance checks."""
	import frappe

	status = {
		doctype: {
			fieldname: frappe.db.get_single_value(doctype, fieldname)
			for fieldname in values
			if frappe.get_meta(doctype).has_field(fieldname)
		}
		for doctype, values in MANAGED_VALUES.items()
	}
	child_doctype = frappe.get_meta("Navbar Settings").get_field("help_dropdown").options
	support_rows = frappe.get_all(
		child_doctype,
		filters={"item_label": ["in", [SUPPORT_ITEM_LABEL, "Frappe Support"]]},
		fields=["item_label", "route"],
		limit=1,
	)
	status["support_item"] = support_rows[0] if support_rows else None
	return status


def extend_bootinfo(bootinfo: dict) -> None:
	"""White-label visible app titles without changing internal app identifiers."""
	for app in bootinfo.get("app_data", []):
		if app.get("app_name") == "frappe":
			app["app_title"] = "MMold Framework"
		elif app.get("app_name") == "erpnext":
			app["app_title"] = "MMold Hub"
