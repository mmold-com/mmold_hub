"""Managed Taiwan localization defaults for MMold Hub sites."""

from __future__ import annotations

import json
from typing import Any


SNAPSHOT_KEY = "mmold_hub.localization.snapshot.v1"

MANAGED_DEFAULTS: dict[str, dict[str, Any]] = {
	"System Settings": {
		"language": "zh-TW",
		"country": "Taiwan",
		"time_zone": "Asia/Taipei",
		"currency": "TWD",
		"date_format": "yyyy-mm-dd",
		"number_format": "#,###.##",
	},
	"Global Defaults": {
		"country": "Taiwan",
		"default_currency": "TWD",
	},
	"Print Settings": {"pdf_page_size": "A4"},
}


def _get_snapshot(frappe) -> dict[str, dict[str, Any]] | None:
	raw = frappe.defaults.get_global_default(SNAPSHOT_KEY)
	return json.loads(raw) if raw else None


def _save_snapshot(frappe, snapshot: dict[str, dict[str, Any]]) -> None:
	frappe.defaults.set_global_default(SNAPSHOT_KEY, json.dumps(snapshot, ensure_ascii=False, sort_keys=True))


def apply_taiwan_defaults(*, force: bool = False) -> dict[str, Any]:
	"""Apply zh-TW defaults once; configured sites require an explicit force."""
	import frappe

	if snapshot := _get_snapshot(frappe):
		return {"status": "already_managed", "snapshot": snapshot}

	setup_complete = bool(frappe.db.get_single_value("System Settings", "setup_complete"))
	if setup_complete and not force:
		return {"status": "skipped_configured_site"}

	snapshot: dict[str, dict[str, Any]] = {}
	for doctype, values in MANAGED_DEFAULTS.items():
		doc = frappe.get_single(doctype)
		snapshot[doctype] = {field: doc.get(field) for field in values}
		for field, value in values.items():
			doc.set(field, value)
		doc.flags.ignore_permissions = True
		doc.save()

	_save_snapshot(frappe, snapshot)
	frappe.translate.clear_cache()
	frappe.clear_cache()
	return {"status": "applied", "snapshot": snapshot, "managed": MANAGED_DEFAULTS}


def restore_taiwan_defaults() -> dict[str, Any]:
	"""Restore only values that are still owned by MMold Hub."""
	import frappe

	snapshot = _get_snapshot(frappe)
	if not snapshot:
		return {"status": "not_managed"}

	restored: dict[str, list[str]] = {}
	skipped: dict[str, list[str]] = {}
	for doctype, original_values in snapshot.items():
		doc = frappe.get_single(doctype)
		for field, original in original_values.items():
			managed_value = MANAGED_DEFAULTS.get(doctype, {}).get(field)
			bucket = restored if doc.get(field) == managed_value else skipped
			bucket.setdefault(doctype, []).append(field)
			if bucket is restored:
				doc.set(field, original)
		doc.flags.ignore_permissions = True
		doc.save()

	frappe.defaults.set_global_default(SNAPSHOT_KEY, None)
	frappe.translate.clear_cache()
	frappe.clear_cache()
	return {"status": "restored", "restored": restored, "skipped": skipped}


def get_localization_status() -> dict[str, Any]:
	"""Return current values for runtime acceptance tests."""
	import frappe

	current = {
		doctype: {field: frappe.db.get_single_value(doctype, field) for field in values}
		for doctype, values in MANAGED_DEFAULTS.items()
	}
	return {"current": current, "expected": MANAGED_DEFAULTS, "managed": bool(_get_snapshot(frappe))}


def merge_custom_translation_messages(
	bootinfo: dict[str, Any], translations: dict[str, str], *, language: str | None = None
) -> bool:
	"""Give the Custom App zh-TW catalog final precedence in Desk boot messages."""
	user = bootinfo.get("user") or {}
	active_language = (language or bootinfo.get("lang") or user.get("language") or "")
	active_language = active_language.replace("_", "-").casefold()
	if active_language != "zh-tw":
		return False

	bootinfo.setdefault("__messages", {}).update(translations)
	return True


def extend_bootinfo_translations(bootinfo: dict[str, Any]) -> None:
	"""Apply this App's zh-TW catalog after all installed App catalogs are merged."""
	import frappe

	# Frappe v16 calls extend_bootinfo hooks before assigning bootinfo["lang"].
	# Resolve the active language from the session/User record at this stage.
	user = bootinfo.get("user") or {}
	language = bootinfo.get("lang") or user.get("language") or frappe.translate.get_user_lang()
	if language.replace("_", "-").casefold() != "zh-tw":
		return

	from frappe.translate import get_translations_from_csv

	translations = get_translations_from_csv("zh-TW", "mmold_hub")
	merge_custom_translation_messages(bootinfo, translations, language=language)


def prefer_guest_zh_tw(response, request) -> None:
	"""Redirect an unconfigured Chinese Guest login to Frappe's native zh-TW route."""
	import frappe

	if request.method != "GET" or request.path != "/login" or frappe.session.user != "Guest":
		return

	if request.args.get("_lang") == "zh-TW":
		response.set_cookie(
			"preferred_language", "zh-TW", max_age=31_536_000, samesite="Lax", secure=False
		)
		return

	preference = request.cookies.get("preferred_language")
	is_simplified_chinese = preference in (None, "", "zh", "zh-CN", "zh_CN", "zh-Hans", "zh_Hans")
	if not is_simplified_chinese:
		return

	response.set_cookie(
		"preferred_language",
		"zh-TW",
		max_age=31_536_000,
		samesite="Lax",
		secure=False,
	)
	response.status_code = 302
	response.headers["Location"] = "/login?_lang=zh-TW"
