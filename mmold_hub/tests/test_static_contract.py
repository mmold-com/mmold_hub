import pathlib
import unittest
import json


PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[2]
PACKAGE_ROOT = PROJECT_ROOT / "mmold_hub"


class TestStaticContract(unittest.TestCase):
	def test_phase_5_print_template_uses_repeating_flow_table(self):
		template = (PACKAGE_ROOT / "templates/print_formats/mmold_transaction.html").read_text()
		self.assertIn("thead { display: table-header-group; }", template)
		self.assertIn("break-inside: avoid", template)
		self.assertIn("https://mmold.com", template)
		self.assertIn("counter(page)", template)
		self.assertNotIn('id="header-html"', template)
		self.assertNotIn('id="footer-html"', template)
	def test_phase_5_job_card_template_shows_manufacturing_context(self):
		template = (PACKAGE_ROOT / "templates/print_formats/mmold_transaction.html").read_text()
		for value in ("doc.get(\"work_order\")", "doc.get(\"production_item\")", "doc.get(\"operation\")", "doc.get(\"workstation\")"):
			self.assertIn(value, template)
		self.assertIn('doc.doctype == "Job Card" and not child_rows', template)
	def test_required_app_files_exist(self):
		for relative_path in (
			"__init__.py",
			"hooks.py",
			"compatibility.py",
			"branding.py",
			"lifecycle.py",
			"localization.py",
			"modules.txt",
			"patches.txt",
			"mmold_hub/.frappe",
		):
			self.assertTrue((PACKAGE_ROOT / relative_path).exists(), relative_path)

	def test_no_core_override_hooks_in_phase_2(self):
		hooks = (PACKAGE_ROOT / "hooks.py").read_text(encoding="utf-8")
		for forbidden in (
			"override_doctype_class",
			"override_whitelisted_methods",
			"doc_events",
			"scheduler_events",
			"auth_hooks",
		):
			self.assertNotIn(forbidden, hooks)

	def test_phase_3_guest_locale_asset_is_enabled(self):
		hooks = (PACKAGE_ROOT / "hooks.py").read_text(encoding="utf-8")
		self.assertIn("web_include_js", hooks)
		self.assertTrue((PACKAGE_ROOT / "public/js/prefer_zh_tw.js").exists())

	def test_phase_3_desk_search_has_zh_tw_custom_app_override(self):
		hooks = (PACKAGE_ROOT / "hooks.py").read_text(encoding="utf-8")
		asset = PACKAGE_ROOT / "public/js/desk_zh_tw.js"
		self.assertIn("desk_zh_tw.js", hooks)
		self.assertTrue(asset.exists())
		contents = asset.read_text(encoding="utf-8")
		self.assertIn('"zh-TW"', contents)
		self.assertIn('#desktop-navbar-modal-search', contents)
		self.assertIn('"aria-label"', contents)
		self.assertIn('setAttribute(attribute, "搜尋")', contents)
		self.assertIn('"data-original-title"', contents)
		self.assertIn('"data-bs-original-title"', contents)
		self.assertIn('aria-description', contents)
		self.assertIn('if (!boot) return "";', contents)
		self.assertIn('["Item Name", "品項名稱"]', contents)
		self.assertIn('["Item 名稱", "品項名稱"]', contents)
		self.assertIn('["Is customer exempted from sales tax?", "此客戶是否免徵營業稅？"]', contents)
		self.assertIn('.list-row-head [data-fieldname="item_name"] [data-sort-by="item_name"]', contents)
		self.assertIn('[data-fieldname="exempt_from_sales_tax"] .label-area', contents)
		item_list = (PACKAGE_ROOT / "public/js/item_list_zh_tw.js").read_text(encoding="utf-8")
		self.assertIn('["Item Name", "Item 名稱"].includes(label)', item_list)
		quotation_form = (PACKAGE_ROOT / "public/js/quotation_form_zh_tw.js").read_text(encoding="utf-8")
		self.assertIn('doctype_js = {"Quotation": "public/js/quotation_form_zh_tw.js"}', hooks)
		self.assertIn('control.set_label?.(label)', quotation_form)
		self.assertIn("apply_when_boot_ready", contents)
		self.assertIn('["選 Item", "選取品項"]', contents)
		self.assertIn('["Select Item", "選取品項"]', contents)
		self.assertIn('["Item 名稱", "品項名稱"]', contents)
		self.assertIn('["模板物料", "範本品項"]', contents)
		self.assertIn('[placeholder*="Item"]', contents)
		self.assertIn('characterData: true', contents)
		self.assertNotIn('query_all(root, "*")', contents)
		self.assertNotIn('document.createTreeWalker(root,', contents)
		self.assertIn("window.setTimeout(flush, 100)", contents)
		self.assertIn('for (const node of record.addedNodes) enqueue(node)', contents)
		self.assertNotIn('new MutationObserver(() => translate_desktop_search())', contents)
		self.assertIn('doctype_list_js = {"Item": "public/js/item_list_zh_tw.js"}', hooks)
		item_list_asset = PACKAGE_ROOT / "public/js/item_list_zh_tw.js"
		self.assertTrue(item_list_asset.exists())
		item_list_contents = item_list_asset.read_text(encoding="utf-8")
		self.assertIn("upstream_onload.call(this, listview)", item_list_contents)
		self.assertIn('frappe.meta.get_docfield("Item", "item_name")', item_list_contents)
		self.assertIn('label: "品項名稱"', item_list_contents)
		self.assertIn("listview.render_header(true)", item_list_contents)
		self.assertLess(contents.index('if (!supported_languages.has(get_current_language())) return;'), contents.index("translate_visible_composite_labels(root);"))
		self.assertIn('["Invoicing", "開票管理"]', contents)
		self.assertIn('["Financial Reports", "財務報表"]', contents)
		self.assertIn('query_all(root, ".desktop-icon img[alt]")', contents)

	def test_phase_3_setup_wizard_defaults_to_zh_tw(self):
		hooks = (PACKAGE_ROOT / "hooks.py").read_text(encoding="utf-8")
		asset = PACKAGE_ROOT / "public/js/setup_wizard_zh_tw.js"
		self.assertIn("setup_wizard_requires", hooks)
		self.assertTrue(asset.exists())
		contents = asset.read_text(encoding="utf-8")
		self.assertIn('language_code = "zh-TW"', contents)
		self.assertIn('fallback_language_name = "繁體中文"', contents)

	def test_phase_4_branding_stays_in_custom_app(self):
		hooks = (PACKAGE_ROOT / "hooks.py").read_text(encoding="utf-8")
		self.assertIn('app_title = "MMold Hub"', hooks)
		self.assertIn("brand_html", hooks)
		self.assertIn("app_logo_url = BRAND_LOGO", hooks)
		self.assertNotIn("add_to_apps_screen", hooks)
		lifecycle = (PACKAGE_ROOT / "lifecycle.py").read_text(encoding="utf-8")
		self.assertIn("remove_apps_screen_shortcut", lifecycle)
		self.assertIn('"app": "mmold_hub"', lifecycle)
		self.assertIn('"link": "/desk"', lifecycle)
		branding = (PACKAGE_ROOT / "branding.py").read_text(encoding="utf-8")
		self.assertIn('SUPPORT_ITEM_LABEL = "MMold Hub Support"', branding)
		self.assertIn('SUPPORT_ITEM_ROUTE = "https://mmold.com"', branding)
		self.assertIn("extend_bootinfo", hooks)
		self.assertIn('app["app_title"] = "MMold Framework"', branding)
		self.assertTrue((PACKAGE_ROOT / "public/images/mmold-hub-logo.png").exists())
		self.assertTrue((PACKAGE_ROOT / "branding.py").exists())
		self.assertTrue((PACKAGE_ROOT / "public/images/pwa-icon-192.png").exists())
		self.assertTrue((PACKAGE_ROOT / "public/images/pwa-icon-512.png").exists())
		self.assertTrue((PACKAGE_ROOT / "public/images/favicon-16.png").exists())
		self.assertTrue((PACKAGE_ROOT / "public/js/brand.js").exists())
		self.assertIn("app_include_js", hooks)
		self.assertNotIn('app_name = "MMold Hub"', hooks)
		brand_script = (PACKAGE_ROOT / "public/js/brand.js").read_text(encoding="utf-8")
		self.assertIn('const brand_name = "MMold Hub"', brand_script)
		self.assertIn('const brand_url = "https://mmold.com"', brand_script)
		self.assertIn('label === "Frappe Framework"', brand_script)
		self.assertIn("redirect_support_menu", brand_script)
		self.assertIn('".frappe-menu .dropdown-menu-item"', brand_script)

	def test_brand_translations_use_taiwan_terms(self):
		translations = (PACKAGE_ROOT / "translations/zh-TW.csv").read_text(encoding="utf-8")
		self.assertIn("ERPNext Settings,設定", translations)
		self.assertIn("Frappe Support,MMold Hub支援", translations)
		self.assertIn("Projects,專案", translations)
		self.assertIn("Items & Pricing,品項與價格", translations)
		for entry in (
			"Customer Name in Arabic,客戶名稱（阿拉伯文）",
			"Is customer exempted from sales tax?,此客戶是否免徵營業稅？",
			"Create Item,建立品項",
			"Item Name,品項名稱",
			"Template Item,範本品項",
			"Template Item Selected,已選取範本品項",
			"Customer Group,客戶群組",
			"Customer Addresses And Contacts,客戶地址與聯絡資訊",
			"Supplier Group,供應商群組",
			"Supplier Addresses And Contacts,供應商地址與聯絡資訊",
			"Items to Order and Receive,待下單與收貨品項",
			"Total Active Items,啟用品項總數",
			"Material Requirements Planning,物料需求規劃",
			"Production Plan,生產計畫",
			"Master Production Schedule,主生產排程",
			"BOM Search,物料清單用途查詢",
			"Promotional Scheme,促銷方案",
			"Product Bundle,產品組合",
			"Quality Inspection Summary,品質檢驗彙總表",
			"Manufactured Items Value,已製造品項金額",
			"Address And Contacts,地址與聯絡資訊",
			"Item Alternative,替代品項",
			"Item Attribute,品項屬性",
			"Item Manufacturer,品項製造商",
			"Itemwise Recommended Reorder Level,品項建議補貨點",
			"Serial No Service Contract Expiry,序號服務合約到期狀態",
			"Production Planning Report,生產計畫報表",
			"Routing,製程路線",
			"Stock Transactions,庫存異動",
			"Stock Reports,庫存報表",
			"Stock Value by Item Group,依品項群組分類的庫存金額",
			"Item-wise Purchase History,品項採購明細",
			"Item Lead Time,品項前置時間",
			"Subcontracted Item To Be Received,待入庫的委外品項",
			"Won Opportunities,成交商機",
			"Switch to Frappe CRM,了解 CRM 方案",
			"Item Group,品項群組",
			"Item Price,品項價格",
			"Items and Pricing,品項與價格",
			"Key Reports,重要報表",
			"POS Profile,POS 設定檔",
			"Terms and Conditions Template,條款與條件範本",
			"Available Stock for Packing Items,包裝品項可用庫存",
			"Item-wise Sales History,品項銷售明細",
			"Item-wise Sales Register,品項銷售臺帳",
			"Pending SO Items For Purchase Request,待採購申請的銷售訂單品項",
			"Sales Person Target Variance Based On Item Group,業務員品項群組目標差異分析",
			"Territory Target Variance Based On Item Group,區域品項群組目標差異分析",
		):
			self.assertIn(entry, translations)
		self.assertIn("報表與主檔</b></span>", translations)
		self.assertNotIn("報表與&amp; 主檔", translations)
		self.assertIn("近 1 個月新增商機", translations)
		self.assertIn("https://mmold.com", translations)
		self.assertIn("MMold Hub</a>", translations)
		self.assertIn("了解 MMold Hub 的 CRM 解決方案。", translations)
		self.assertIn("MMold Hub Support,MMold Hub支援", translations)
		self.assertIn("Reset Desktop Layout,重設桌面版面", translations)
		self.assertIn("Frappe Framework Version,MMold Framework 版本", translations)
		for entry in (
			'"Support",售後服務',
			'"Warranty",保固',
			'"Warranty Claim",保固申請',
			'"Service Level Agreement",服務水準協議',
			'"Switch to Helpdesk",切換至客服服務台',
		):
			self.assertIn(entry, translations)

	def test_phase_3_accounting_and_finance_terms_use_taiwanese_translations(self):
		translations = (PACKAGE_ROOT / "translations/zh-TW.csv").read_text(encoding="utf-8")
		for entry in (
			"Accounting Dimension,會計維度",
			"Accounting Dimensions,會計維度",
			"Accounting Dimension Detail,會計維度明細",
			"Accounting Dimension Filter,會計維度篩選器",
			"Consider Accounting Dimensions,納入會計維度",
			"Inventory Dimension,庫存維度",
			"Default Dimension,預設維度",
			"Dimension Name,維度名稱",
			"Enable Item-wise Inventory Account,啟用品項別庫存科目",
			"Tax Masters,稅務主檔",
			"Review Accounts Settings,檢視會計設定",
			"Review Chart of Accounts,檢視會計科目表",
			"Reconciliation Takes Effect On,核銷生效日",
			"Only Include Allocated Payments,僅包含已分配（已核銷）的付款",
			"Party is required create a payment entry.,建立收付款憑證時必須指定往來對象。",
			"Please set Fiscal Code for the customer '%s',請為客戶 %s 設定稅務識別碼",
			"Please set Fiscal Code for the public administration '%s',請為公部門機關 %s 設定稅務識別碼",
			"The selected change account {} doesn't belongs to Company {}.,所選找零科目 {} 不屬於公司 {}。",
			"The currency of invoice {} ({}) is different from the currency of this dunning ({}).",
			"Row #{}: POS Invoice {} is not submitted yet",
			"Row {0}: Quantity not available for {4} in warehouse {1} at posting time of the entry ({2} {3})",
			"To cancel a {} you need to cancel the POS Closing Entry {}.",
			"You need to cancel POS Closing Entry {} to be able to cancel this document.",
		):
			self.assertIn(entry, translations)
		self.assertNotIn("輔助核算", translations)

	def test_about_dialog_branding_and_version_policy(self):
		from mmold_hub import __version__

		self.assertEqual(__version__, "6.37.0")
		brand_script = (PACKAGE_ROOT / "public/js/brand.js").read_text(encoding="utf-8")
		self.assertIn('a[href*="github.com"]', brand_script)
		self.assertIn('if (name === "ERPNext") row.remove()', brand_script)
		self.assertIn("MMold Consulting Ltd.", brand_script)
		self.assertIn("Frappe Technologies Pvt. Ltd.", brand_script)

	def test_phase_5_print_formats_are_registered_as_fixtures(self):
		hooks = (PACKAGE_ROOT / "hooks.py").read_text(encoding="utf-8")
		for doctype in (
			"Quotation", "Sales Order", "Delivery Note", "Sales Invoice", "Purchase Order",
			"Purchase Receipt", "Purchase Invoice", "Stock Entry", "Work Order", "Job Card",
		):
			self.assertIn(f"MMold Hub - {doctype}", hooks)
		formats = json.loads((PACKAGE_ROOT / "fixtures/print_format.json").read_text())
		template = (PACKAGE_ROOT / "templates/print_formats/mmold_transaction.html").read_text()
		self.assertEqual(len(formats), 10)
		self.assertTrue(all(row["html"] == template for row in formats))
		self.assertTrue(all(row["pdf_generator"] == "chrome" and row["print_designer"] == 0 for row in formats))


if __name__ == "__main__":
	unittest.main()
