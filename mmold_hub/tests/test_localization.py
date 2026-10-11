import csv
import pathlib
import unittest

from mmold_hub.localization import MANAGED_DEFAULTS, merge_custom_translation_messages


class TestLocalizationContract(unittest.TestCase):
	def test_taiwan_erp_terms_use_context_specific_entry_translations(self):
		catalog_path = pathlib.Path(__file__).resolve().parents[1] / "translations/zh-TW.csv"
		with catalog_path.open(encoding="utf-8", newline="") as handle:
			rows = list(csv.reader(handle))
			translations = {row[0]: row[1] for row in rows if len(row) >= 2}
			context_translations = {(row[0], row[2]): row[1] for row in rows if len(row) == 3}

		self.assertEqual(translations["POS Profile required to make POS Entry"], "建立 POS 單據需要 POS 設定檔")
		self.assertEqual(translations["Domain Settings"], "領域設定")
		self.assertEqual(context_translations[("Domain Name", "Domain")], "領域名稱")
		self.assertEqual(context_translations[("Domain Name", "Email Domain")], "Domain Name")
		self.assertEqual(context_translations[("Domain", "Company")], "領域")
		self.assertEqual(context_translations[("Domain", "Email Account")], "網域")
		self.assertEqual(translations["Please select Company and Posting Date to getting entries"], "請選擇公司與過帳日期以取得分錄")
		self.assertEqual(
			translations["Used to create an opening Stock Entry with the Valuation Rate when the item is saved"],
			"儲存品項時，使用計價率建立期初庫存異動單。",
		)

	def test_doctype_context_translation_overrides_are_present(self):
		catalog_path = pathlib.Path(__file__).resolve().parents[1] / "translations/zh-TW.csv"
		with catalog_path.open(encoding="utf-8", newline="") as handle:
			translations = {(row[0], row[2] if len(row) == 3 else ""): row[1] for row in csv.reader(handle)}

		self.assertEqual(translations[("Item Name", "Item")], "品項名稱")
		self.assertEqual(translations[("Item 名稱", "Item")], "品項名稱")
		self.assertEqual(
			translations[("Is customer exempted from sales tax?", "Quotation")],
			"此客戶是否免徵營業稅？",
		)

	def test_taiwan_defaults(self):
		self.assertEqual(MANAGED_DEFAULTS["System Settings"]["language"], "zh-TW")
		self.assertEqual(MANAGED_DEFAULTS["System Settings"]["time_zone"], "Asia/Taipei")
		self.assertEqual(MANAGED_DEFAULTS["Global Defaults"]["default_currency"], "TWD")
		self.assertEqual(MANAGED_DEFAULTS["Print Settings"]["pdf_page_size"], "A4")

	def test_gregorian_date_format(self):
		self.assertEqual(MANAGED_DEFAULTS["System Settings"]["date_format"], "yyyy-mm-dd")

	def test_custom_catalog_overrides_merged_zh_tw_messages(self):
		bootinfo = {
			"lang": "zh_TW",
			"__messages": {"Item Name": "Item 名稱", "Projects": "專案"},
		}
		merged = merge_custom_translation_messages(
			bootinfo,
			{"Item Name": "品項名稱", "Item 名稱": "品項名稱", "Projects": "專案"},
		)

		self.assertTrue(merged)
		self.assertEqual(bootinfo["__messages"]["Item Name"], "品項名稱")
		self.assertEqual(bootinfo["__messages"]["Item 名稱"], "品項名稱")

	def test_custom_catalog_does_not_override_other_languages(self):
		bootinfo = {"lang": "en", "__messages": {"Item Name": "Item Name"}}

		self.assertFalse(merge_custom_translation_messages(bootinfo, {"Item Name": "品項名稱"}))
		self.assertEqual(bootinfo["__messages"]["Item Name"], "Item Name")

	def test_custom_catalog_uses_user_language_before_boot_lang_is_assigned(self):
		bootinfo = {
			"user": {"language": "zh-TW"},
			"__messages": {"Item Name": "Item 名稱"},
		}

		merged = merge_custom_translation_messages(bootinfo, {"Item Name": "品項名稱"})

		self.assertTrue(merged)
		self.assertEqual(bootinfo["__messages"]["Item Name"], "品項名稱")

	def test_custom_catalog_accepts_resolved_session_language(self):
		bootinfo = {"__messages": {"Item Name": "Item 名稱"}}

		merged = merge_custom_translation_messages(
			bootinfo, {"Item Name": "品項名稱"}, language="zh_TW"
		)

		self.assertTrue(merged)
		self.assertEqual(bootinfo["__messages"]["Item Name"], "品項名稱")


if __name__ == "__main__":
	unittest.main()
