(() => {
	const key = "preferred_language";
	const preference = document.cookie
		.split(";")
		.map((part) => part.trim())
		.find((part) => part.startsWith(`${key}=`))
		?.split("=")[1];
	const shouldPreferTaiwan =
		!preference || ["zh", "zh-CN", "zh_CN", "zh-Hans", "zh_Hans"].includes(preference);

	const pageLanguage = document.documentElement.lang;
	if (
		shouldPreferTaiwan &&
		["zh", "zh-CN", "zh_CN", "zh-Hans", "zh_Hans"].includes(pageLanguage)
	) {
		document.cookie = `${key}=zh-TW; Path=/; Max-Age=31536000; SameSite=Lax`;
		const target = new URL(window.location.href);
		target.searchParams.set("_lang", "zh-TW");
		window.location.replace(target.toString());
	}
})();
