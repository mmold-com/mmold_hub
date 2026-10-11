"""Rollback-only Phase 5 ERPNext document and print-format checks.

Run with ``bench --site mmold-test.localhost execute
mmold_hub.tests.phase5_acceptance.run_purchase_order``. No document is
committed, and this module refuses to run on any other site.
"""

from io import BytesIO

import frappe
from pypdf import PdfReader


TEST_SITE = "mmold-test.localhost"
COMPANY = "綠品有限公司"
SUPPLIER_NAME = "PHASE5 臨時測試供應商"
STOCK_ITEM = "PHASE5-STOCK-ACCEPTANCE"
FINISHED_ITEM = "PHASE5-FG-ACCEPTANCE"
RAW_ITEM = "PHASE5-RM-ACCEPTANCE"
WORKSTATION_NAME = "Phase 5 Acceptance Workstation"
OPERATION_NAME = "Phase 5 Acceptance Operation"


def _render_pdf(doc):
	pdf = frappe.get_print(
		doc.doctype,
		doc.name,
		print_format=f"MMold Hub - {doc.doctype}",
		as_pdf=True,
	)
	if not isinstance(pdf, bytes) or not pdf.startswith(b"%PDF"):
		frappe.throw(f"{doc.doctype} did not produce a valid PDF")
	pages = PdfReader(BytesIO(pdf)).pages
	page_sizes_ok = all(
		abs(float(page.mediabox.width) - 595.28) < 2
		and abs(float(page.mediabox.height) - 841.89) < 2
		for page in pages
	)
	text = "\n".join(page.extract_text() or "" for page in pages)
	logos = len(pages[0].images) if pages else 0
	table_field = "required_items" if doc.doctype == "Work Order" else "items"
	rows = doc.get(table_field) or []
	first_marker = next(
		(row.get("item_code") or row.get("operation") for row in rows if row.get("item_code") or row.get("operation")),
		None,
	)
	compact_text = "".join(text.split()).replace("-", "")
	marker_ok = not first_marker or "".join(str(first_marker).split()).replace("-", "") in compact_text
	manufacturing_values = (
		doc.get("work_order"),
		doc.get("production_item"),
		doc.get("operation"),
		doc.get("workstation"),
	)
	manufacturing_context_ok = doc.doctype != "Job Card" or all(
		value and "".join(str(value).split()).replace("-", "") in compact_text
		for value in manufacturing_values
	)
	content_ok = (
		"MMold Hub" in text
		and "mmold.com" in text
		and doc.name in text
		and marker_ok
		and manufacturing_context_ok
	)
	if not pages or not page_sizes_ok or not logos or not content_ok:
		frappe.throw(
			f"{doc.doctype} PDF checks failed: pages={len(pages)}, A4={page_sizes_ok}, "
			f"logos={logos}, content={content_ok}, item_marker={marker_ok}, "
			f"manufacturing_context={manufacturing_context_ok}"
		)
	return {
		"doctype": doc.doctype,
		"docstatus": doc.docstatus,
		"pdf_bytes": len(pdf),
		"pages": len(pages),
		"a4": page_sizes_ok,
		"logos": logos,
		"brand_text_ok": content_ok,
		"rows": len(rows),
		"manufacturing_context_ok": manufacturing_context_ok,
		"no_persistent_changes": True,
	}


def _run_draft(doctype, values, prerequisites=()):
	if frappe.local.site != TEST_SITE:
		frappe.throw(f"Phase 5 acceptance is restricted to {TEST_SITE}")

	savepoint = "phase5_acceptance"
	frappe.db.savepoint(savepoint)
	try:
		for prerequisite in prerequisites:
			frappe.get_doc(prerequisite).insert(ignore_permissions=True)

		doc = frappe.get_doc({"doctype": doctype, **values})
		doc.insert(ignore_permissions=True)
		return _render_pdf(doc)
	finally:
		frappe.db.rollback(save_point=savepoint)


def run_quotation():
	return _run_draft(
		"Quotation",
		{
			"quotation_to": "Customer",
			"party_name": "PHASE5 測試客戶 MMold",
			"company": COMPANY,
			"items": [{"item_code": "PHASE5-PRINT-001", "qty": 1, "rate": 3500}],
		},
	)


def run_delivery_note():
	return _run_draft(
		"Delivery Note",
		{
			"customer": "PHASE5 測試客戶 MMold",
			"company": COMPANY,
			"items": [{"item_code": "PHASE5-PRINT-001", "qty": 1, "rate": 3500}],
		},
	)


def run_sales_invoice():
	return _run_draft(
		"Sales Invoice",
		{
			"customer": "PHASE5 測試客戶 MMold",
			"company": COMPANY,
			"items": [
				{
					"item_code": "PHASE5-PRINT-001",
					"qty": 1,
					"rate": 3500,
					"income_account": "7488 - 其他營業外收入—其他 - MMold",
				}
			],
		},
	)


def run_existing_sales_order():
	if frappe.local.site != TEST_SITE:
		frappe.throw(f"Phase 5 acceptance is restricted to {TEST_SITE}")

	orders = frappe.get_all("Sales Order", pluck="name", limit=20)
	if not orders:
		frappe.throw("No existing Sales Order is available for read-only print validation")
	docs = [frappe.get_doc("Sales Order", name) for name in orders]
	doc = max(docs, key=lambda order: len(order.items))
	return _render_pdf(doc)


def run_all_document_checks():
	if frappe.local.site != TEST_SITE:
		frappe.throw(f"Phase 5 acceptance is restricted to {TEST_SITE}")

	checks = (
		run_quotation,
		run_existing_sales_order,
		run_delivery_note,
		run_sales_invoice,
		run_purchase_order,
		run_purchase_receipt,
		run_purchase_invoice,
		run_stock_entry,
		run_work_order,
		run_job_card,
	)
	results = []
	for check in checks:
		try:
			results.append(check())
		except Exception as error:
			results.append({"check": check.__name__, "error": str(error)})
	return results


def run_purchase_order():
	return _run_draft(
		"Purchase Order",
		{
			"company": COMPANY,
			"supplier": SUPPLIER_NAME,
			"transaction_date": "2026-10-03",
			"items": [
				{
					"item_code": "PHASE5-PRINT-001",
					"qty": 1,
					"rate": 3500,
					"schedule_date": "2026-10-10",
					"expense_account": "5611 - 勞務成本 - MMold",
					"cost_center": "主 - MMold",
				}
			],
		},
		prerequisites=(
			{
				"doctype": "Supplier",
				"supplier_name": SUPPLIER_NAME,
				"supplier_group": "Services",
				"supplier_type": "Company",
			},
		),
	)


def _supplier_prerequisite():
	return (
		{
			"doctype": "Supplier",
			"supplier_name": SUPPLIER_NAME,
			"supplier_group": "Services",
			"supplier_type": "Company",
		},
	)


def run_purchase_receipt():
	return _run_draft(
		"Purchase Receipt",
		{
			"company": COMPANY,
			"supplier": SUPPLIER_NAME,
			"items": [{"item_code": "PHASE5-PRINT-001", "qty": 1, "rate": 3500}],
		},
		prerequisites=_supplier_prerequisite(),
	)


def run_purchase_invoice():
	return _run_draft(
		"Purchase Invoice",
		{
			"company": COMPANY,
			"supplier": SUPPLIER_NAME,
			"items": [
				{
					"item_code": "PHASE5-PRINT-001",
					"qty": 1,
					"rate": 3500,
					"expense_account": "5611 - 勞務成本 - MMold",
					"cost_center": "主 - MMold",
				}
			],
		},
		prerequisites=_supplier_prerequisite(),
	)


def _stock_item_prerequisite():
	return (
		{
			"doctype": "Item",
			"item_code": STOCK_ITEM,
			"item_name": "Phase 5 Stock Acceptance",
			"item_group": "Products",
			"stock_uom": "Nos",
			"is_stock_item": 1,
			"is_sales_item": 0,
			"is_purchase_item": 0,
		},
	)


def run_stock_entry():
	return _run_draft(
		"Stock Entry",
		{
			"company": COMPANY,
			"stock_entry_type": "Material Receipt",
			"purpose": "Material Receipt",
			"items": [
				{
					"item_code": STOCK_ITEM,
					"qty": 1,
					"t_warehouse": "倉庫 - MMold",
					"basic_rate": 3500,
				}
			],
		},
		prerequisites=_stock_item_prerequisite(),
	)


def _create_manufacturing_context():
	for item_code, item_name, is_sales_item, is_purchase_item in (
		(RAW_ITEM, "Phase 5 Acceptance Raw Material", 0, 1),
		(FINISHED_ITEM, "Phase 5 Acceptance Finished Good", 1, 0),
	):
		frappe.get_doc(
			{
				"doctype": "Item",
				"item_code": item_code,
				"item_name": item_name,
				"item_group": "Products",
				"stock_uom": "Nos",
				"is_stock_item": 1,
				"is_sales_item": is_sales_item,
				"is_purchase_item": is_purchase_item,
			}
		).insert(ignore_permissions=True)

	workstation = frappe.get_doc(
		{
			"doctype": "Workstation",
			"workstation_name": WORKSTATION_NAME,
			"production_capacity": 1,
			"warehouse": "進行中 - MMold",
			"hour_rate": 0,
		}
	).insert(ignore_permissions=True)
	operation = frappe.get_doc(
		{
			"doctype": "Operation",
			"name": OPERATION_NAME,
			"workstation": workstation.name,
			"total_operation_time": 15,
		}
	).insert(ignore_permissions=True)
	bom = frappe.get_doc(
		{
			"doctype": "BOM",
			"company": COMPANY,
			"item": FINISHED_ITEM,
			"quantity": 1,
			"uom": "Nos",
			"currency": "TWD",
			"conversion_rate": 1,
			"with_operations": 1,
			"operations": [
				{
					"operation": operation.name,
					"workstation": workstation.name,
					"time_in_mins": 15,
				}
			],
			"items": [
				{
					"item_code": RAW_ITEM,
					"qty": 1,
					"uom": "Nos",
					"rate": 3500,
					"source_warehouse": "倉庫 - MMold",
				}
			],
		}
	).insert(ignore_permissions=True)
	bom.submit()
	work_order = frappe.get_doc(
		{
			"doctype": "Work Order",
			"company": COMPANY,
			"production_item": FINISHED_ITEM,
			"bom_no": bom.name,
			"qty": 1,
			"planned_start_date": "2026-10-03 10:00:00",
			"source_warehouse": "倉庫 - MMold",
			"wip_warehouse": "進行中 - MMold",
			"fg_warehouse": "成品 - MMold",
		}
	).insert(ignore_permissions=True)
	return bom, operation, workstation, work_order


def run_work_order():
	if frappe.local.site != TEST_SITE:
		frappe.throw(f"Phase 5 acceptance is restricted to {TEST_SITE}")

	savepoint = "phase5_work_order_acceptance"
	frappe.db.savepoint(savepoint)
	try:
		_, _, _, doc = _create_manufacturing_context()
		return _render_pdf(doc)
	finally:
		frappe.db.rollback(save_point=savepoint)


def run_job_card():
	if frappe.local.site != TEST_SITE:
		frappe.throw(f"Phase 5 acceptance is restricted to {TEST_SITE}")

	savepoint = "phase5_job_card_acceptance"
	frappe.db.savepoint(savepoint)
	try:
		_, operation, workstation, work_order = _create_manufacturing_context()
		work_order.submit()
		doc = frappe.get_doc(
			{
				"doctype": "Job Card",
				"work_order": work_order.name,
				"company": COMPANY,
				"operation": operation.name,
				"workstation": workstation.name,
				"for_quantity": 1,
			}
		).insert(ignore_permissions=True)
		return _render_pdf(doc)
	finally:
		frappe.db.rollback(save_point=savepoint)
