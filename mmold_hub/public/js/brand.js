(() => {
	"use strict";

	const brand_name = "MMold Hub";
	const brand_url = "https://mmold.com";
	const external_brand_hosts = new Set([
		"frappe.io",
		"support.frappe.io",
		"erpnext.com",
		"frappecloud.com",
	]);

	function is_brand_host(hostname) {
		return [...external_brand_hosts].some(
			(host) => hostname === host || hostname.endsWith(`.${host}`)
		);
	}

	function query_all(root, selector) {
		const elements = [];
		if (root instanceof Element && root.matches(selector)) elements.push(root);
		root.querySelectorAll?.(selector).forEach((element) => elements.push(element));
		return elements;
	}

	function apply_branding(root = document) {
		query_all(root, "#brand-logo, .sidebar-header .header-logo img").forEach((logo) => {
			logo.src = "/assets/mmold_hub/images/mmold-hub-logo.png";
			logo.alt = brand_name;
		});

		query_all(root, "a[href]").forEach((link) => {
			try {
				const url = new URL(link.href, window.location.origin);
				if (is_brand_host(url.hostname)) {
					link.href = brand_url;
				}
			} catch {
				// Leave invalid or non-HTTP links untouched.
			}
		});

		query_all(root, ".about-frappe-section img.about-frappe-wordmark").forEach((logo) => {
			logo.src = "/assets/mmold_hub/images/mmold-hub-logo.png";
			logo.alt = brand_name;
			logo.classList.add("about-mmold-hub-wordmark");
		});

		query_all(root, ".sidebar-header .header-subtitle").forEach((subtitle) => {
			const label = subtitle.textContent.trim();
			if (label === "Frappe Framework") subtitle.textContent = "MMold Framework";
			else if (["ERPNext", "Frappe"].includes(label)) subtitle.textContent = brand_name;
		});

		query_all(root, ".about-info-title").forEach((title) => {
			if (title.textContent.trim() === "Frappe Framework Version") {
				title.textContent = "MMold Framework Version";
			}
		});

		query_all(root, '.about-social-btns a[href*="github.com"]').forEach((link) => {
			link.remove();
		});

		query_all(root, ".about-app-row").forEach((row) => {
			const name = row.querySelector(".about-app-name")?.textContent?.trim();
			if (name === "ERPNext") row.remove();
		});

		query_all(root, "#about-framework-version").forEach((version) => {
			version.textContent = version.textContent.replace(/^frappe:/i, "MMold Framework:");
		});

		query_all(root, ".about-footer").forEach((footer) => {
			if (!footer.textContent.includes("MMold Consulting Ltd.")) {
				// Keep the upstream copyright attribution visible for license compliance.
				footer.textContent =
					"© MMold Consulting Ltd. | © Frappe Technologies Pvt. Ltd. 與貢獻者";
			}
		});

		if (window.location.pathname === "/desk/support") {
			const support_terms = new Map([
				["售後支持", "售後服務"],
				["售後支持設定", "售後服務設定"],
				["质量保证", "保固管理"],
				["保修申請", "保固申請"],
				["服務水平協議", "服務水準協議"],
				["問題類型", "案件類型"],
				["問題優先級", "案件優先級"],
				["問題", "客服案件"],
				["維護巡修計劃", "維護保養排程"],
				["維護巡修", "維護巡檢"],
				["報表與& 主檔", "報表與主檔"],
				["Frappe Helpdesk", "MMold Hub 客服服務台"],
			]);
			query_all(root, "*").forEach((element) => {
				if (element.children.length) return;
				const current = element.textContent.trim();
				if (support_terms.has(current)) element.textContent = support_terms.get(current);
			});
		}

		if (document.title && /^(ERPNext|Frappe)(\s|$)/i.test(document.title)) {
			document.title = document.title.replace(/^(ERPNext|Frappe)/i, brand_name);
		}
	}

	// Frappe's avatar-menu support item calls window.open() from an inline
	// callback, so there is no href for the normal external-link rewrite above.
	function redirect_support_menu(event) {
		const item = event.target.closest?.(".frappe-menu .dropdown-menu-item");
		const title = item?.querySelector(".menu-item-title")?.textContent?.trim();
		if (!["MMold Hub支援", "Frappe Support"].includes(title)) return;

		event.preventDefault();
		event.stopImmediatePropagation();
		if (typeof window.open === "function") {
			window.open(brand_url, "_blank", "noopener");
		} else {
			window.location.assign(brand_url);
		}
	}

	function start() {
		apply_branding();
		document.addEventListener("click", redirect_support_menu, true);
		const pending_roots = new Set();
		let scheduled = false;
		const flush = () => {
			scheduled = false;
			const roots = [...pending_roots];
			pending_roots.clear();
			for (const root of roots) apply_branding(root);
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
			attributeFilter: ["href"],
			childList: true,
			subtree: true,
		});
	}

	if (document.readyState === "loading") {
		document.addEventListener("DOMContentLoaded", start, { once: true });
	} else {
		start();
	}
})();
