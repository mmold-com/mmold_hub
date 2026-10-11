# MMold Hub

MMold Hub 是以 Frappe／ERPNext 為基礎的客製 App，將台灣繁體中文、MMold 品牌介面與列印格式集中管理，讓客製內容與上游 Core 分離。

## 功能

- 提供台灣繁體中文介面與術語調整。
- 套用 MMold Hub 品牌資產與介面設定。
- 提供 MMold Hub 專用 Jinja 列印格式。
- 在安裝與升級階段檢查 Frappe／ERPNext 相容版本。

## 相容版本

- ERPNext `v16.37.0`
- Frappe `v16.36.0`
- MMold Hub App `6.37.0`

請先確認現有 Bench 與 Site 使用相容版本，再安裝此 App。

## 安裝

在 Frappe Bench 目錄取得 App，並安裝至指定 Site：

```sh
bench get-app https://github.com/mmold-com/mmold_hub.git
bench --site <site-name> install-app mmold_hub
```

升級時依 Frappe／ERPNext 的標準流程備份 Site，更新 App 後執行 migration，並在正式環境套用前先於隔離 Site 驗證。

## 開發

App 程式位於 `mmold_hub/`。版本與相容性設定位於 `pyproject.toml`；繁體中文翻譯及列印格式分別位於 `mmold_hub/translations/` 與 `mmold_hub/templates/`。

此 App 不修改 Frappe、ERPNext 或第三方 App Core。新增客製功能時，請優先使用 Frappe 提供的 hooks、fixtures、patches 與擴充點。
