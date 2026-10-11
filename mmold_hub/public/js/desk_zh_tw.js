(() => {
	"use strict";

	const supported_languages = new Set(["zh-TW", "zh_TW"]);
	const desktop_icon_translations = new Map([
		["Framework", "框架"],
		["Organization", "組織"],
		["Invoicing", "開票管理"],
		["Payments", "付款"],
		["Financial Reports", "財務報表"],
		["Accounts Setup", "會計設定"],
		["Taxes", "稅"],
		["Banking", "銀行"],
		["Budget", "預算"],
		["Share Management", "股份管理"],
		["Subscription", "訂閱"],
		["Assets", "資產"],
		["Buying", "採購"],
		["Manufacturing", "生產"],
		["Projects", "專案"],
		["Quality", "品質"],
		["Selling", "銷售"],
		["Stock", "庫存"],
		["Subcontracting", "委外"],
		["ERPNext Settings", "設定"],
	]);

	function query_all(root, selector) {
		const elements = [];
		if (root instanceof Element && root.matches(selector)) elements.push(root);
		root.querySelectorAll?.(selector).forEach((element) => elements.push(element));
		return elements;
	}

	function query_first(root, selector) {
		if (root instanceof Element && root.matches(selector)) return root;
		return root.querySelector?.(selector) || null;
	}

	function get_current_language() {
		const boot = window.frappe?.boot;
		if (!boot) return "";

		return (
			boot.user?.language ||
			boot.sysdefaults?.language ||
			boot.lang ||
			document.documentElement.lang ||
			""
		);
	}

	function register_zh_tw_datepicker_language() {
		const datepicker = window.jQuery?.fn?.datepicker;
		if (!datepicker?.language) return;

		datepicker.language["zh-TW"] = {
			days: ["星期日", "星期一", "星期二", "星期三", "星期四", "星期五", "星期六"],
			daysShort: ["週日", "週一", "週二", "週三", "週四", "週五", "週六"],
			daysMin: ["日", "一", "二", "三", "四", "五", "六"],
			months: [
				"一月", "二月", "三月", "四月", "五月", "六月",
				"七月", "八月", "九月", "十月", "十一月", "十二月",
			],
			monthsShort: [
				"1 月", "2 月", "3 月", "4 月", "5 月", "6 月",
				"7 月", "8 月", "9 月", "10 月", "11 月", "12 月",
			],
			today: "今天",
			clear: "清除",
			dateFormat: "yyyy-mm-dd",
			timeFormat: "hh:ii aa",
			firstDay: 0,
		};
	}

	function translate_visible_datepicker(root = document) {
		if (!supported_languages.has(get_current_language())) return;

		const picker =
			(root instanceof Element && root.closest(".datepicker.active")) ||
			query_first(root, ".datepicker.active");
		if (!picker) return;

		const nav_title = picker.querySelector(".datepicker--nav-title");
		const year = nav_title?.querySelector("i")?.textContent.trim();
		const month_match = nav_title?.textContent.match(/\b(January|February|March|April|May|June|July|August|September|October|November|December)\b/);
		if (nav_title && year && month_match) {
			const month_index = [
				"January", "February", "March", "April", "May", "June",
				"July", "August", "September", "October", "November", "December",
			].indexOf(month_match[1]);
			if (month_index >= 0) {
				nav_title.innerHTML = `<i>${year}</i> 年 ${month_index + 1} 月`;
			}
		}

		const weekdays = ["日", "一", "二", "三", "四", "五", "六"];
		picker.querySelectorAll(".datepicker--day-name").forEach((day, index) => {
			day.textContent = weekdays[index % 7];
			day.setAttribute("title", `星期${weekdays[index % 7]}`);
		});
		const today = picker.querySelector('.datepicker--button[data-action="today"]');
		if (today) today.textContent = "今天";
	}

	function translate_quill_controls(root = document) {
		if (!supported_languages.has(get_current_language())) return;

		const toolbar_labels = new Map([
			["bold", "粗體"],
			["italic", "斜體"],
			["underline", "底線"],
			["strike", "刪除線"],
			["blockquote", "引言"],
			["code-block", "程式碼區塊"],
			["direction: rtl", "由右至左"],
			["link", "連結"],
			["image", "圖片"],
			["list: ordered", "編號清單"],
			["list: bullet", "項目符號清單"],
			["list: check", "核取方塊清單"],
			["indent: -1", "減少縮排"],
			["indent: +1", "增加縮排"],
			["clean", "清除格式"],
		]);
		for (const button of query_all(root, ".ql-toolbar button[aria-label]")) {
			const label = toolbar_labels.get(button.getAttribute("aria-label"));
			if (label) button.setAttribute("aria-label", label);
		}
	}

	function translate_chart_month_labels(root = document) {
		if (!supported_languages.has(get_current_language())) return;

		const month_numbers = new Map([
			["Jan", 1], ["January", 1], ["Feb", 2], ["February", 2],
			["Mar", 3], ["March", 3], ["Apr", 4], ["April", 4],
			["May", 5], ["Jun", 6], ["June", 6], ["Jul", 7],
			["July", 7], ["Aug", 8], ["August", 8], ["Sep", 9],
			["Sept", 9], ["September", 9], ["Oct", 10], ["October", 10],
			["Nov", 11], ["November", 11], ["Dec", 12], ["December", 12],
		]);
		const labels = query_all(root, ".frappe-chart svg text, .chart-container svg text");
		for (const label of labels) {
			const original = label.textContent.trim();
			const match = original.match(/^(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:t|tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)(?:\s+(\d{4}))?(?:\s*\((?:Amount|金額)\))?$/);
			if (!match) continue;

			const month = month_numbers.get(match[1]);
			if (!month) continue;
			const amount_suffix = /\((?:Amount|金額)\)$/.test(original) ? "（金額）" : "";
			const localized_month = match[2] ? `${match[2]} 年 ${month} 月` : `${month} 月`;
			label.textContent = `${localized_month}${amount_suffix}`;
		}
	}

	function translate_desktop_search(root = document) {
		const is_zh_tw = supported_languages.has(get_current_language());
		document.documentElement.classList.toggle("mmold-hub-zh-tw", is_zh_tw);
		if (!is_zh_tw) return;
		register_zh_tw_datepicker_language();
		translate_visible_datepicker(root);
		translate_quill_controls(root);
		translate_chart_month_labels(root);
		translate_visible_composite_labels(root);

		const icon_images = query_all(root, ".desktop-icon img[alt]");
		for (const image of icon_images) {
			const translated_alt = desktop_icon_translations.get(image.alt);
			if (translated_alt) image.alt = translated_alt;
		}

		const button = query_first(root, "#desktop-navbar-modal-search");
		if (!button) return;

		for (const attribute of [
			"title",
			"aria-label",
			"data-original-title",
			"data-bs-original-title",
		]) {
			if (button.hasAttribute(attribute) && button.getAttribute(attribute) !== "搜尋") {
				button.setAttribute(attribute, "搜尋");
			}
		}
		if (button.getAttribute("aria-description") !== "搜尋") {
			button.setAttribute("aria-description", "搜尋");
		}

		const label = button.querySelector(".desktop-search-icon");
		if (!label || label.textContent.trim() === "搜尋") return;

		const text_node = Array.from(label.childNodes).find(
			(node) => node.nodeType === Node.TEXT_NODE && node.textContent.trim()
		);
		if (text_node) {
			text_node.textContent = text_node.textContent.replace(/\bSearch\b/g, "搜尋");
		} else {
			label.append(document.createTextNode(" 搜尋"));
		}
	}

	function translate_visible_composite_labels(root = document) {
		const item_name_header = query_first(root,
			'.list-row-head [data-fieldname="item_name"] [data-sort-by="item_name"]'
		);
		if (item_name_header && /^(Item Name|Item 名稱)$/.test(item_name_header.textContent.trim())) {
			item_name_header.textContent = "品項名稱";
			item_name_header.setAttribute("title", "點選以依品項名稱排序");
		}

		const sales_tax_exemption_label = query_first(root,
			'[data-fieldname="exempt_from_sales_tax"] .label-area'
		);
		if (
			sales_tax_exemption_label?.textContent.trim() === "Is customer exempted from sales tax?"
		) {
			sales_tax_exemption_label.textContent = "此客戶是否免徵營業稅？";
		}

		const mixed_language_labels = new Map([
			["Item Name", "品項名稱"],
			["Item 名稱", "品項名稱"],
			["Is customer exempted from sales tax?", "此客戶是否免徵營業稅？"],
			["模板物料", "範本品項"],
			["模板 Item", "範本品項"],
			["已選範本 Item", "已選取範本品項"],
			["選 Item", "選取品項"],
			["Select Item", "選取品項"],
		]);
		const labeled_elements = query_all(root,
			'[placeholder*="Item"], [title*="Item"], [aria-label*="Item"], ' +
			'[placeholder*="sales tax"], [title*="sales tax"], [aria-label*="sales tax"], ' +
			'[placeholder*="模板"], [title*="模板"], [aria-label*="模板"]'
		);
		for (const element of labeled_elements) {
			for (const attribute of ["placeholder", "title", "aria-label"]) {
				const value = element.getAttribute(attribute);
				const translated_value = mixed_language_labels.get(value?.trim());
				if (translated_value) element.setAttribute(attribute, translated_value);
			}
		}

		const elements = query_all(root,
			'.list-row-head [data-fieldname="item_name"], ' +
			'[data-fieldname="exempt_from_sales_tax"] .label-area, ' +
			'.modal-title, .control-label, .btn, .dropdown-item'
		);
		for (const element of elements) {
			const translated_value = mixed_language_labels.get(element.textContent.trim());
			if (!translated_value) continue;
			const walker = document.createTreeWalker(element, NodeFilter.SHOW_TEXT);
			let text_node;
			let first_text = true;
			while ((text_node = walker.nextNode())) {
				if (!text_node.textContent.trim()) continue;
				text_node.textContent = first_text ? translated_value : "";
				first_text = false;
			}
		}
		// Generic labels come from the zh-TW catalog. Never walk every DOM text
		// node on Desk boot: each mutation can otherwise rescan the whole page.
	}

	function start() {
		const pending_roots = new Set();
		let scheduled = false;
		const flush = () => {
			scheduled = false;
			const roots = [...pending_roots];
			pending_roots.clear();
			for (const root of roots) translate_desktop_search(root);
		};
		const enqueue = (node) => {
			const root = node instanceof Element ? node : node?.parentElement;
			if (root) pending_roots.add(root);
			if (!scheduled && pending_roots.size) {
				scheduled = true;
				window.setTimeout(flush, 100);
			}
		};
		const observer = new MutationObserver((records) => {
			for (const record of records) {
				if (record.type === "attributes" || record.type === "characterData") enqueue(record.target);
				for (const node of record.addedNodes) enqueue(node);
			}
		});
		observer.observe(document.documentElement, {
			attributes: true,
			characterData: true,
			attributeFilter: [
				"title",
				"aria-label",
				"aria-description",
				"alt",
				"data-original-title",
				"data-bs-original-title",
				"placeholder",
			],
			childList: true,
			subtree: true,
		});

		let attempts = 0;
		const apply_when_boot_ready = () => {
			if (!window.frappe?.boot) {
				if (attempts++ < 100) window.setTimeout(apply_when_boot_ready, 50);
				return;
			}
			translate_desktop_search(document);
		};
		apply_when_boot_ready();
	}

	if (document.readyState === "loading") {
		document.addEventListener("DOMContentLoaded", start, { once: true });
	} else {
		start();
	}
})();
