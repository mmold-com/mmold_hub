"""Idempotent MMold Hub application lifecycle hooks."""

from mmold_hub.compatibility import validate_runtime
from mmold_hub.branding import apply_branding_defaults, restore_branding_defaults
from mmold_hub.localization import apply_taiwan_defaults, restore_taiwan_defaults


def _logger():
	import frappe

	return frappe.logger("mmold_hub", allow_site=True)


def before_install() -> None:
	validate_runtime()
	_logger().info("MMold Hub compatibility validation passed before install")


def after_install() -> None:
	result = apply_taiwan_defaults()
	branding = apply_branding_defaults()
	_logger().info("MMold Hub installed; localization=%s branding=%s", result["status"], branding["status"])


def before_migrate() -> None:
	validate_runtime()
	_logger().info("MMold Hub compatibility validation passed before migrate")


def after_migrate() -> None:
	result = apply_taiwan_defaults()
	branding = apply_branding_defaults()
	removed_shortcuts = remove_apps_screen_shortcut()
	_logger().info(
		"MMold Hub migration completed; localization=%s branding=%s removed_shortcuts=%s",
		result["status"],
		branding["status"],
		removed_shortcuts,
	)


def remove_apps_screen_shortcut() -> int:
	"""Remove the legacy MMold Hub Apps Screen tile without touching other icons."""
	import frappe

	filters = {
		"label": "MMold Hub",
		"app": "mmold_hub",
		"icon_type": "App",
		"link_type": "External",
		"link": "/desk",
	}
	names = frappe.get_all("Desktop Icon", filters=filters, pluck="name")
	for name in names:
		frappe.delete_doc("Desktop Icon", name, ignore_permissions=True)
	return len(names)


def before_uninstall() -> None:
	result = restore_taiwan_defaults()
	branding = restore_branding_defaults()
	_logger().info("MMold Hub uninstall started; localization=%s branding=%s", result["status"], branding["status"])
