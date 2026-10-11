"""Phase 5 MMold Hub document print formats."""

from __future__ import annotations

import frappe


PRINT_DOCTYPES = (
	"Quotation",
	"Sales Order",
	"Delivery Note",
	"Sales Invoice",
	"Purchase Order",
	"Purchase Receipt",
	"Purchase Invoice",
	"Stock Entry",
	"Work Order",
	"Job Card",
)


def create_transaction_formats() -> list[str]:
	"""Install/update the ten dedicated formats on an isolated test site."""
	template_path = frappe.get_app_path("mmold_hub", "templates", "print_formats", "mmold_transaction.html")
	html = frappe.read_file(template_path)
	created = []
	for doctype in PRINT_DOCTYPES:
		name = f"MMold Hub - {doctype}"
		if not frappe.db.exists("Print Format", name):
			print_format = frappe.new_doc("Print Format")
			print_format.name = name
			print_format.doc_type = doctype
			print_format.module = "MMold Hub"
			print_format.standard = "No"
			print_format.custom_format = 1
			print_format.print_format_type = "Jinja"
			print_format.print_format_for = "DocType"
			print_format.owner = "Administrator"
		else:
			print_format = frappe.get_doc("Print Format", name)
		print_format.html = html
		print_format.print_designer = 0
		print_format.pdf_generator = "chrome"
		print_format.margin_top = 13
		print_format.margin_bottom = 14
		print_format.margin_left = 12
		print_format.margin_right = 12
		print_format.disabled = 0
		print_format.save(ignore_permissions=True)
		created.append(name)
	frappe.db.commit()
	frappe.clear_cache(doctype="Print Format")
	return created
