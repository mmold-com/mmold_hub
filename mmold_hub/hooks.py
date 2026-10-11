from . import __version__ as app_version

app_name = "mmold_hub"
app_title = "MMold Hub"
app_publisher = "MMold Hub"
app_description = "MMold Hub custom application for ERPNext"
app_email = ""
app_license = "MIT"

# User-facing product identity. `app_name` above remains the immutable Python
# package identifier used by Frappe.
BRAND_LOGO = "/assets/mmold_hub/images/mmold-hub-logo.png"
app_logo_url = BRAND_LOGO
brand_html = (
	'<span class="mmold-hub-brand"><img src="'
	+ BRAND_LOGO
	+ '" alt="MMold Hub" class="mmold-hub-brand-logo">'
	+ "MMold Hub</span>"
)
app_home = "/desk"

# ERPNext is an explicit runtime dependency. No Frappe or ERPNext Core files
# are modified by this App.
required_apps = ["erpnext"]

# Guest pages otherwise prefer a generic browser Accept-Language (for example
# `zh`) over System Settings. This small public asset selects zh-TW only when
# the visitor has not already made an explicit language choice.
web_include_js = [
	"/assets/mmold_hub/js/prefer_zh_tw.js?v=20261002-4",
	"/assets/mmold_hub/js/brand.js?v=20261006-1",
]
after_request = ["mmold_hub.localization.prefer_guest_zh_tw"]

# Frappe's setup wizard language field uses language names while System
# Settings stores a language code. Normalize the managed zh-TW default without
# changing the Core setup wizard or preventing a user from choosing another
# language.
setup_wizard_requires = "assets/mmold_hub/js/setup_wizard_zh_tw.js"

# Desk-side branding and user-facing external-link policy.
app_include_js = [
	"/assets/mmold_hub/js/brand.js?v=20261006-1",
	"/assets/mmold_hub/js/desk_zh_tw.js?v=20261007-21",
]
app_include_css = ["/assets/mmold_hub/css/brand.css?v=20261007-5"]

# Item's standard ListView rebuilds its header after global Desk assets run.
# Extend that DocType's list script while preserving ERPNext's native handlers.
doctype_js = {"Quotation": "public/js/quotation_form_zh_tw.js"}
doctype_list_js = {"Item": "public/js/item_list_zh_tw.js"}

# Frappe builds the active app title into Desk boot data before sidebar render.
# This Hook changes only user-facing display titles, not package identifiers.
extend_bootinfo = [
	"mmold_hub.branding.extend_bootinfo",
	"mmold_hub.localization.extend_bootinfo_translations",
]

# Lifecycle hooks remain limited to version validation and logging. Print
# formats are delivered as app-owned fixtures; no Core overrides are used.
before_install = "mmold_hub.lifecycle.before_install"
after_install = "mmold_hub.lifecycle.after_install"
before_migrate = "mmold_hub.lifecycle.before_migrate"
after_migrate = "mmold_hub.lifecycle.after_migrate"
before_uninstall = "mmold_hub.lifecycle.before_uninstall"

fixtures = [
	{
		"dt": "Print Format",
		"filters": [
			["name", "in", [
				"MMold Hub - Quotation",
				"MMold Hub - Sales Order",
				"MMold Hub - Delivery Note",
				"MMold Hub - Sales Invoice",
				"MMold Hub - Purchase Order",
				"MMold Hub - Purchase Receipt",
				"MMold Hub - Purchase Invoice",
				"MMold Hub - Stock Entry",
				"MMold Hub - Work Order",
				"MMold Hub - Job Card",
			]],
		],
	},
]
