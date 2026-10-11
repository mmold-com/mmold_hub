(() => {
	"use strict";

	const label = "此客戶是否免徵營業稅？";
	const is_zh_tw = () =>
		[frappe.boot?.lang, frappe.boot?.user?.language]
			.filter(Boolean)
			.some((language) => ["zh-tw", "zh_tw"].includes(language.toLowerCase()));

	function translate_sales_tax_exemption_label(frm) {
		if (!is_zh_tw()) return;

		const docfield = frappe.meta.get_docfield(
			"Quotation",
			"exempt_from_sales_tax",
			frm.doc.name
		);
		if (docfield) docfield.label = label;

		const control = frm.fields_dict?.exempt_from_sales_tax;
		if (control) {
			control.df.label = label;
			control.set_label?.(label);
		}
	}

	frappe.ui.form.on("Quotation", {
		setup: translate_sales_tax_exemption_label,
		onload: translate_sales_tax_exemption_label,
		refresh: translate_sales_tax_exemption_label,
	});
})();
