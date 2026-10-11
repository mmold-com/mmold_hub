# Phase 7 — Production Image（AMD64）

## 目標與界線

QNAP TS-464 為 `linux/amd64`；使用者已確認核心版號採官方 ERPNext v16.37.0。本機為 Apple Silicon macOS（ARM64），OrbStack Buildx 已恢復並提供 AMD64 emulation。此階段只建置與驗收本機 AMD64 Image，不建立正式 Site、不啟動正式 Compose、不推送 Registry，也不部署或連線正式 QNAP。

## 固定輸入

- ERPNext v16.37.0，官方 Tag commit：`af63cde4941570ec7b9e12422c68302762cfcf91`。
- 官方基底：`frappe/erpnext@sha256:9ed12ab3e685e896637aa3598dd9acc653b84db9e00b59520ba7960dec35a450`（`linux/amd64`）；已從 Docker Hub 拉取。
- Frappe v16.36.0，官方 Tag commit：`f3f0c0b13c77a419487150a198fed42964e1919e`，符合 ERPNext `pyproject.toml` 的 `>=16.21.0,<17.0.0`，且已由官方映像 `bench version` 實測。
- MMold Hub `6.37.0`；ERPNext 主版號減 10，次版與修補版同步。Runtime compatibility guard 已更新。
- Print Designer v1.6.7；PDF on Submit 不納入。
- Python 3.14.7、Chromium 154.0.8037.57 已在官方 AMD64 基底實測；Node.js 24.21.0 固定於 Node 官方 AMD64 image digest；Yarn 1.22.22 由 Corepack 指定。

## 建置方式

```sh
docker buildx build --platform linux/amd64 \
  -f docker/production/Dockerfile \
  -t mmold-hub/erpnext:v16.37.0-mmold.6.37.0-pd1.6.7-amd64-zh-twfix47 \
  --load .
```

Print Designer v1.6.7 安裝鉤子固定檢查 `frappe-bench/chromium/chrome-linux/headless_shell`；本映像將該路徑連至基底映像內已安裝的 `/usr/bin/chromium-headless-shell`，避免 Site 安裝時另行下載 Chromium。QNAP Compose 同時必須使用 Print Designer 實際支援的全域設定鍵 `chromium_binary_path`。fix47 需在 Docker API 可用後重新建置及驗證，並以新的封存匯入 NAS；fix46 維持歷史版本，不覆寫或刪除。

Dockerfile 的建置 Context allowlist 排除環境檔、Secret、研究資料與 PDF on Submit；映像沿用官方 Frappe Docker Entrypoint/CMD，供同一映像未來分別執行 backend、frontend、websocket、worker 與 scheduler。

## AMD64 驗收

1. [x] 官方基底 `bench version`、Python、Chromium 版本確認。
2. [x] Build Custom Image，`docker image inspect` 確認 `linux/amd64` 並記錄 Image ID。
3. [x] Bench App 清單確認 Frappe、ERPNext、mmold_hub、Print Designer；PDF on Submit 不存在。
4. [x] Python 鎖定相依及 Print Designer frozen-lockfile 前端建置完成。
5. [x] Noto CJK／fontconfig 確認，含繁中與英文的 A4 headless PDF smoke test 通過。
6. [x] 備份隔離 Site 後執行 migration；Desk 與登入路徑 runtime 通過，未碰正式資料。
7. [x] QNAP Compose 只做本機語法與拓樸檢視；未在 QNAP 建立資料夾、Site 或服務。

## 目前狀態

- OrbStack Docker API 可用；Docker Server 為 `linux/arm64`，Buildx 可輸出 `linux/amd64`。
- 官方 ERPNext v16.37.0 多架構 manifest 已固定，AMD64 digest 成功使用。
- Custom Image 已建置：`mmold-hub/erpnext:v16.37.0-mmold.6.37.0-pd1.6.7-amd64`，Image ID `sha256:dc39af4ef260ecd81ebdfe5ffe7dfc00080296a644754bb9f9bf958e98a2335d`，平台 `linux/amd64`。
- Runtime 實測版本：Frappe 16.36.0、ERPNext 16.37.0、mmold_hub 6.37.0、Print Designer 1.6.7；PDF on Submit 不存在。
- 建置工具 Node.js 24.21.0、Yarn 1.22.22 已固定並成功完成 frontend assets build。
- 隔離 Site 已在備份後完成 v16.37.0 migration；重建六個 app service 後，版本、App 清單、runtime guard、登入 URL HTTP 200 及 Desk 均通過。
- Chromium 154.0.8037.57 識別 Noto Sans CJK TC；繁中／英文 PDF A4 尺寸 smoke test 通過。
- App 單元測試 18/18 通過；隔離 Compose 使用 `MMOLD_TEST_IMAGE` 覆寫 Production Image 的路徑已補上。
- Compose 與 QNAP 路徑只在本機做靜態／語法查核；QNAP 未連線、未部署、未建立目錄或容器。
- [x] 使用者完成隔離測試站互動登入；2026-10-06 依指示重設本機隔離 Site `Administrator` 密碼並登出舊工作階段，密碼不寫入文件或 Repository。發現英文介面原因為 System Settings.language=`en`、Administrator.language 空白；修正為 `zh-TW`，時區設為 `Asia/Taipei`，清除快取並回查符合預設。Desk 模組捷徑、使用者選單與搜尋文字／提示均已目視及 Accessibility 驗證為繁中；為修正搜尋按鈕靜態 title，新 Custom App-only 資產已在隔離站載入。QNAP／正式環境未操作。
- 為隔離 Site 翻譯回歸另建本機驗證映像 `mmold-hub/erpnext:v16.37.0-mmold.6.37.0-pd1.6.7-amd64-zh-twfix6`（Image manifest SHA256：`d1d8581e062134111a0245de164a0b3aea7f634411462fa0e6c3ffedec9a8cb5`）。這是原 AMD64 production image 的本機測試衍生標籤，不覆寫原正式候選映像、不推送 Registry、不部署 QNAP。只重建隔離站 app services 並清除該 Site 快取；MariaDB／Redis 持久資料未刪除或重建，未執行 migration。
- Phase 3 後續無障礙標籤回歸使用新本機映像 `mmold-hub/erpnext:v16.37.0-mmold.6.37.0-pd1.6.7-amd64-zh-twfix7`（Image ID／manifest list：`sha256:2f91294cfe9162bf1494232cfed6c94fdc036eb677cd3060cc942f96acd92dfb`；本機載入平台 `linux/amd64`）。在既有隔離 Site 重建 frontend、backend、websocket、queue-short、queue-long、scheduler 六個 App 服務後，清除該 Site Frappe 快取並實際重載確認搜尋列及工作區圖示 alt 繁中。DB、Redis、Site volumes 未刪除或重建，未執行 installer 或 migration；映像未推送、不取代原 production candidate、不部署 QNAP。
- 隨後因銷售側欄 `Items & Pricing` 發現上游混合語系，另建最新 zh-TW 回歸映像 `mmold-hub/erpnext:v16.37.0-mmold.6.37.0-pd1.6.7-amd64-zh-twfix8`（Image ID／manifest list：`sha256:b5111cb5a75b6abbc0ba237a7679f12fa61cb8300c4602c18c1e142518a154ca`；`linux/amd64`）。隔離站確認「品項與價格」正確顯示；仍只更新六個 App 服務，未碰 MariaDB／Redis／Site volumes、未 migration、未部署 QNAP。
- 此前 v16.36.0 ARM64 Image 保留為歷史驗收產物，不推送且不視為 QNAP 相容。
- Phase 6 MCP 按使用者指示不測試；Phase 8 QNAP 已進入實機驗收，部署仍須逐項確認影響與資料保護條件。

### 2026-10-08 fix47 修正與封裝

- 因 QNAP Site 初始化時 Print Designer `setup_chromium()` 找不到 Bench 預期的 `chromium/chrome-linux/headless_shell` 而嘗試下載失敗，Dockerfile 已加入該路徑指向系統 Chromium 的 symlink；Compose 改用 PDF generator 實際讀取的 `chromium_binary_path`。
- fix47 Image：`mmold-hub/erpnext:v16.37.0-mmold.6.37.0-pd1.6.7-amd64-zh-twfix47`，Image ID／manifest list `sha256:cfd7feca920a3c51b82878508651a2411b0e9ba9ba226a036903df22a39f5d9b`，`linux/amd64`，約 1.04 GB。
- 唯讀容器驗證 symlink 存在且可執行、實際目標 `/usr/bin/chromium-headless-shell`、Chromium `154.0.8037.57`；`bench version` 確認 Frappe 16.36.0、ERPNext 16.37.0、mmold_hub 6.37.0、Print Designer 1.6.7。兩份 QNAP Compose `config --quiet` 均通過。
- 產物：`dist/mmold-hub-erpnext-v16.37.0-mmold.6.37.0-pd1.6.7-amd64-zh-twfix47-docker.tar.gz`（SHA-256 `840e993ec74947fca5b0e78c1409048c6adceb1436a7ac4afcb343442e01eef3`），封存內為單一 Docker image、30 layers，gzip 完整性通過；部署範本 ZIP `dist/mmold-hub-qnap-deploy-v16.37.0-fix47.zip`（SHA-256 `d4bfb8a0726a58ee2bc3614deaf2e98f815b4000cf61069664d3a7ff1eb7e599`），ZIP 完整性通過且不含 `.env` 秘密檔。
- QNAP Container Station 已匯入 fix47（畫面標籤完整、狀態「未使用」）；目前 `mmold-hub` 服務仍使用 fix46，尚未以 fix47 重建。此次匯入不是部署或 runtime 驗收證據。
- QNAP 現況另經 File Station 只讀檢查：`sites/hub.mmold.com` 空白；`hub.mmold.com.mount-target-20261008` 含 `locks/`、`logs/`、`private/`、`public/` 與 `site_config.json`，屬部分初始化殘留；`hub.mmold.com.partial-20261008` 空白。`backups/` 與 `secrets/` 皆空白。MariaDB 與 Redis named volumes 正在使用中，必須保留。尚未執行 migration、bootstrap、檔案搬移或資料庫修改。
- 因尚無可驗證的站台／資料庫備份，暫停所有會重建服務、初始化 Site 或寫入資料庫的步驟；需先建立並驗證安全備份，再個別核准 fix47 套用與 Site 修復。

## 回復

本輪版本升級只變更 Custom App 版本契約、Production Image 基底引用、QNAP Image tag 及文件。v16.36.0 ARM64 Image 與先前記錄保留；隔離 Site migration 前先完成 database 與 files 備份，沒有覆寫正式 Site、資料庫或 QNAP 資料。若需回復隔離資料，使用 migration 前備份整組還原；僅將 Image tag 降回舊版不足以回復資料庫 schema。
