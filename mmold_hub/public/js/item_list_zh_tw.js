(() => {
	"use strict";

	const settings = (frappe.listview_settings["Item"] ||= {});
	const upstream_onload = settings.onload;

	settings.onload = function (listview) {
		if (typeof upstream_onload === "function") {
			upstream_onload.call(this, listview);
		}

		const language = (frappe.boot?.lang || frappe.boot?.user?.language || "")
			.replace("_", "-")
			.toLowerCase();
		if (language !== "zh-tw") return;

		const item_name_field = frappe.meta.get_docfield("Item", "item_name");
		if (item_name_field && ["Item Name", "Item 名稱"].includes(item_name_field.label)) {
			item_name_field.label = "品項名稱";
		}

		let label_changed = false;
		listview.columns = listview.columns.map((column) => {
			const label = column.df?.label?.trim();
			if (column.df?.fieldname !== "item_name" && !["Item Name", "Item 名稱"].includes(label)) {
				return column;
			}
			label_changed = true;
			return { ...column, df: { ...column.df, label: "品項名稱" } };
		});

		if (label_changed) listview.render_header(true);
	};
})();
