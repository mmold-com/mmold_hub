(() => {
	"use strict";

	const language_code = "zh-TW";
	const fallback_language_name = "繁體中文";

	function get_language_name() {
		return (
			frappe.setup?.data?.lang?.codes_to_names?.[language_code] || fallback_language_name
		);
	}

	function normalize_managed_language_default() {
		const current_language = frappe.wizard?.values?.language;
		if (!current_language || current_language === language_code) {
			frappe.wizard.values.language = get_language_name();
		}
	}

	frappe.setup.on("before_load", () => {
		const welcome_slide = frappe.setup.slides_settings.find(
			(slide) => slide.name === "welcome"
		);
		const language_field = welcome_slide?.fields?.find(
			(field) => field.fieldname === "language"
		);

		if (language_field) {
			language_field.default = get_language_name();
		}
	});

	const load_prefilled_data = frappe.setup.utils.load_prefilled_data;
	frappe.setup.utils.load_prefilled_data = function (slide, callback) {
		return load_prefilled_data.call(this, slide, (loaded_slide) => {
			normalize_managed_language_default();
			callback(loaded_slide);
		});
	};
})();
