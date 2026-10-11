# Phase 8 — QNAP Container Station 部署範本

## 範圍

使用 Browser Use 對 QNAP `192.168.1.110` 確認：QTS `5.2.10.3577`、Container Station `3.1.2.1742`、機型 TS-464。QTS File Station 顯示 `DataVol1/Container`；Container Station 儲存空間頁的既有掛載路徑為 `/share/CACHEDEV1_DATA/Container/container-station-data/...`，據此確認可見實體父路徑為 `/share/CACHEDEV1_DATA/Container`。2026-10-08 已在專用 `mmold-hub/` 下建立 Compose 所需目錄，並逐一確認 ACL：擁有者 `mmold` 保留讀／寫／執行，群組與公開的讀／寫／執行均關閉；未勾選遞迴套用。Compose frontend 依使用者要求設為 NAS LAN `0.0.0.0:8088`；不開啟路由器轉埠或 Internet 公開。2026-10-08 Container Station 已成功匯入 fix46 AMD64 ERPNext 映像。

2026-10-08 fix47 已由使用者匯入 QNAP Container Station，但尚未套用。即時只讀檢查確認 `mmold-hub` 的 9 個常駐服務仍使用 fix46，configurator 已停止，應用程式狀態為「其他」；MariaDB／Redis named volumes 均「使用中」。File Station 顯示 `sites/hub.mmold.com` 空白；`hub.mmold.com.mount-target-20261008` 有 `locks/`、`logs/`、`private/`、`public/` 與 `site_config.json`；`hub.mmold.com.partial-20261008` 空白。`backups/` 空白；`secrets/` 有兩個預期檔案（只記錄檔名與大小，未讀取內容）。QTS 配額頁即時顯示 `mmold` 配額 500 GB、已用 102.0595 GB、尚可用 397.9404 GB；儲存與快照總管顯示 DataVol1 可用約 2.8 TB。因此並無證據顯示一般使用者配額或整體磁碟空間已滿。兩個已停止的單次 bootstrap 應用程式均使用 fix46：較早建立的 `mmold-hub-site-bootstrap-once` 記錄顯示 Frappe installer 在讀取 `apps.txt` 時遇到 `OSError: apps.txt Not Found`；較晚的 `mmold-hub-bootstrap-v6` 記錄則顯示 Print Designer v1.6.7 的 `setup_chromium()` 建立 `/home/frappe/frappe-bench/config/print_designer_chromium_setup.lock` 時回報 `OSError: [Errno 122] Disk quota exceeded`。本機目前 `deploy/qnap/compose.yaml` 與 `compose.container-station.yaml` 均未將 `/home/frappe/frappe-bench/config` 掛載至 QNAP；故錯誤較可能位於容器可寫層或其底層 quota，但尚無直接驗證，不能下定論。現有 `deploy/qnap/README.md` 曾記載已新增 config bind mount，與兩份 Compose 實際內容不符；此為待修正／確認的文件落差，本輪未改 Compose 或建立 QNAP config 資料夾。這些是兩次初始化執行各自的明確中止原因；不能據此判斷資料庫一致性。Container Station 顯示 frontend 對外映射 `8088 → 8080/TCP`，瀏覽器顯示登入頁；只驗證連接埠與畫面回應，未輸入帳密或提交登入。唯讀查看 MariaDB 記錄時，反覆看到來自 app network 的資料庫帳號驗證拒絕；backend 記錄則看到 request timeout、Redis socket/read traceback，以及 worker timeout 後以 SIGKILL 結束、再啟動新 worker。這些觀察顯示目前即使有登入頁也不能視為後端健康；Site／DB 對應、憑證與資源壓力等根因尚未區分。此次未讀取 site config 或 secrets 內容，未啟動／移除 bootstrap、未變更容器、資料庫、Site 或任何 volume；禁止直接重跑 bootstrap、遷移資料或自行搬移／覆寫殘留檔案。

**目前堆疊已啟動，Site 初始化與登入驗收尚未完成。** 2026-10-08 經使用者確認，在 Container Station 移除舊 `mmold-hub` 應用程式時未勾選「自動移除連接到容器的自行定義儲存空間及匿名儲存空間」。移除後立即核對，`mmold-hub-mariadb` 與 `mmold-hub-redis-queue` 均仍存在；以修正版 Compose 重建後兩者狀態轉為「使用中」，掛載路徑不變。重建的 10 個容器中，MariaDB、兩個 Redis、backend、frontend、queue-short、queue-long、scheduler、websocket 均顯示執行中；一次性 `configurator` 已停止（Compose 相依服務已啟動）。修正版已在 NAS Container Station YAML 驗證器通過，且確認初始化命令會在缺少 `sites/common_site_config.json` 時先建立空 JSON。當時先前一次瀏覽 `http://192.168.1.110:8088/` 曾收到 Frappe 404「hub.mmold.com does not exist」；後續即時檢查已確認此連接埠映射至 frontend 並顯示登入頁。Site 目錄與初始化殘留仍不一致，實際登入及功能尚未驗收，不可視為上線完成。

QNAP 上原始 GUI 範本仍存於 `DataVol1/Container/mmold-hub/compose.container-station.yaml`；經驗證後，Container Station 中的應用程式 Compose 設定已以本機修正版重建（在建立應用程式草稿中貼上完整修正版並以綠色勾號通過）。NAS 上的原始範本檔案尚未同步這次修正，日後需維護時應一併更新，避免檔案與實際應用設定不一致。MariaDB／Redis named volumes 保留並重新掛載；QTS 全域進階資料夾權限維持關閉、ACL 未變更。Phase 8 尚未完成。

另存時曾產生雙份 YAML（13.00 KB）；已改名隔離為 `compose.container-station.duplicate-20261008.yaml`，未刪除。原始檔另保留為 `compose.container-station.pre-named-volumes-20261008.yaml`（6.55 KB）。正式檔已確認單份大小 6.46 KB。這兩份隔離備份均不得用於部署。

## 新增內容

- `deploy/qnap/compose.yaml`：一般 Docker Compose 版本，使用所有資料 bind mounts。
- `deploy/qnap/compose.container-station.yaml`：Container Station GUI 版本；MariaDB／queue Redis 使用 local named volumes，其餘必要路徑使用 bind mounts。
- `deploy/qnap/.env.example`：QNAP base path 留白，正式密碼改由唯讀 secret files 注入。
- `deploy/qnap/bootstrap_site.py`：明確啟用的 `bootstrap` profile，拒絕覆寫既有 Site，以 Frappe v16 site installer API 建立 ERPNext、MMold Hub 與 Print Designer。
- `deploy/qnap/README.md`：前置條件、啟動、初始化、備份及尚未完成實機驗收項目。

## 網路與持久化

- `db` 和 Redis 僅加入內部 `data` network；backend／workers 只透過內部網路存取資料服務。
- frontend 依使用者最新指示發布 `0.0.0.0:8088` 供 LAN 連線，並連接未來 Tunnel 可加入的 `edge` network；不設定路由器轉埠。Phase 9 才加入 cloudflared。
- Site volume 保存站台設定、公用／私人附件；MariaDB 與 queue Redis 由 Container Station local named volume 持久保存，logs 與 backups 使用 QNAP bind mount。Redis cache 可重建，不持久化。
- 無任何 `ports` 對外發布 3306、6379、8000 或 9000。

## 版本鎖定

| Service | 固定版本／識別 |
|---|---|
| MMold Hub app image | fix46（Image ID `12a5cf8098af`）仍由 9 個常駐服務使用；fix47（Image ID `5bb9945e8e82`）已匯入 QNAP、狀態「未使用」 |
| MariaDB | `11.8.9-noble` amd64 manifest `sha256:de4cf325ed1fc8a22460b4f285de7b9e06d89edbd593505e678ec480f86e501b`；已匯入 QNAP，Container Station Image ID `cc7f5fdd7c8f` |
| Redis | `8.6.7-alpine` amd64 manifest `sha256:019e4fb3c6de024c8f70ab5219d4abded5f335de770876981c7b0a051c43df87`；已匯入 QNAP，Container Station Image ID `166f6f1437e3` |

AMD64 應用程式 Image 已在本機建置及完成 Phase 7 技術驗收，尚未推送 Registry。fix46 Image、MariaDB 與 Redis 固定 digest 已匯入 QNAP。原 Compose 草稿先通過 Container Station YAML 驗證；之後已建立應用程式與 volumes，現況和啟動失敗根因詳見本文件開頭。不得以舊映像或轉譯方式冒用。

## 初步檢查

### 目錄權限核實矩陣（File Station ACL，2026-10-08）

| NAS 目錄 | Compose 用途 | 容器內目標 | 已知執行身分 | 目前證據／狀態 | 下一步門檻 |
|---|---|---|---|---|---|
| `sites/` | Frappe Site、附件 | `/home/frappe/frappe-bench/sites` | Frappe `1000:1000` | File Station 保存後：owner `mmold` rwx；group/public 權限關閉 | 隔離寫入測試；不能單憑 File Station ACL 推定容器 UID 映射 |
| `logs/` | Frappe logs | `/home/frappe/frappe-bench/logs` | Frappe `1000:1000` | File Station 保存後：owner `mmold` rwx；group/public 權限關閉；歷史容器 stat 曾為 `1000:100`、`777`（ACL 修改前） | 隔離寫入測試；歷史 `777` 不代表目前底層權限已驗證 |
| `backups/` | Site 備份 | `/home/frappe/frappe-bench/backup` | Frappe `1000:1000` | File Station 保存後：owner `mmold` rwx；group/public 權限關閉 | 隔離寫入測試；另確認備份目的地及保護措施 |
| Container Station volume `mmold-hub-mariadb` | MariaDB 資料庫 | `/var/lib/mysql` | digest 內 `mysql=999:999` | Container Station 顯示「使用中」；可用 Site 尚未完成，部分初始化殘留另待唯讀資料庫核對 | 建立並驗證一致性備份／還原，再盤點資料庫狀態 |
| Container Station volume `mmold-hub-redis-queue` | Redis queue 持久化 | `/data` | digest 內 `redis=999:1000` | Compose 已建立並掛載；Redis 容器正在執行 | 驗證重啟持久性與排程佇列 |
| `secrets/` | MariaDB／bootstrap 唯讀機密掛載 | `/run/secrets` | `site-bootstrap` 為 Frappe `1000:1000`；MariaDB entrypoint 以 root 讀取 root password file | File Station 有兩個預期檔名；內容未讀取，容器存取權限未驗證 | 驗證 File Station 權限、唯讀掛載及必要讀取能力，其他使用者不可讀 |

本機唯讀檢查已確認 MariaDB `mysql=999:999`、Redis `redis=999:1000`。QNAP 隔離探測實際以 `999:999` 嘗試向兩個 bind mount 寫入均失敗；測試容器已移除。GUI 版本改用 Container Station 管理的 local named volume，不更改 QTS ACL。2026-10-08 移除應用程式時保留 volumes，修正版重建後 Container Station 再次顯示兩者「使用中」並掛載於原路徑；MariaDB 資料目錄完成初始化。Configurator 的缺檔問題已透過 Compose 修正，後續服務均顯示執行中。volume 重啟持久性仍待驗收；目前正式 Site 目錄空白，mount-target 有部分初始化殘留，尚未確認可用 Site。

2026-10-08 已確認 QTS「啟動進階資料夾權限」與 Windows ACL 均未勾選；使用者明確要求維持關閉。`mariadb/`、`redis-queue/` bind mount 測試失敗，已停止使用。修正後 local named volume Compose 已通過本機及 NAS GUI 驗證，並以未刪除 volumes 的方式重建應用程式；目前兩個 volumes 均重新掛載，服務已啟動。早期檢查時 `8088` 曾回應 Frappe 404，當時推測原因是 Site 尚未建立；本輪確認 frontend 映射正確且登入頁可載入，但正式 Site 子目錄仍空白、mount-target 有部分初始化資料，尚不能判定 Site／資料庫一致。Site 建立會初始化 MariaDB schema 並安裝 ERPNext、MMold Hub、Print Designer；此步驟具資料寫入效果，應先確認秘密檔案權限、備份與還原規劃，再透過受控 bootstrap 執行。不能刪除或重建任何既有資料。

- 本機 Docker Compose：v5.1.2。
- Docker Compose v5.1.2 對目前正式範本執行 `config --quiet` 通過；目前拓樸僅 frontend 發布 LAN `8088`，data/app network 為 internal，且未將密碼放入 Compose environment。
- Site bootstrap Python 語法通過；2 項 guard 測試通過（拒絕非法 site name、拒絕既有 site path），未呼叫安裝或資料庫操作。
- MMold Hub App 測試 18/18、compileall、`git diff --check` 通過。
- 舊 ARM64 service image IDs／registry manifest 曾經確認；固定的 AMD64 MariaDB／Redis digest 已匯入並在 QNAP 容器中運作，映像清單顯示 MariaDB `11.8.9-noble` ID `cc7f5fdd7c8f`、Redis `8.6.7-alpine` ID `166f6f1437e3`。NAS 上 MariaDB／Redis 正常進入執行狀態；容器內 UID/GID 與 volume 重啟持久性仍待專項驗收。
- QNAP Container Station 3.1.2.1742 的建立應用程式 YAML 驗證器不會自動讀取 `.env`，GUI 專用變體因此明確填入非機密路徑與固定映像資訊。原 configurator 因 `common_site_config.json` 缺檔而失敗；已由修正版建立缺少的空 JSON 後成功完成相依啟動。使用者確認後，移除舊應用時保留兩個 named volumes，並以修正版重建；當時 10 個容器已建立，9 個長期服務顯示執行中、一次性 configurator 已停止。歷史某次瀏覽器檢查曾收到 Frappe 404；以本文件開頭的 2026-10-08 最新盤點為準：入口目前顯示登入頁，實際登入未測。變體不含密碼字串，只引用唯讀 secret 檔。一般工作沙箱曾拒絕 Docker socket；當時核准唯讀通道 Docker API 回報 Docker Server `linux/arm64`／29.4.0。
- Production Image 本機 inspect 確認為 `linux/amd64`，Image ID `sha256:dc39af4ef260ecd81ebdfe5ffe7dfc00080296a644754bb9f9bf958e98a2335d`；唯讀、不掛載資料的暫時容器確認 Frappe 使用者為 `1000:1000`，容器已自動移除。Compose 鎖定的 MariaDB `11.8.9-noble` 與 Redis `8.6.7-alpine` 已在本機取得精確 digest、轉成 Container Station 相容封存格式並匯入 QNAP；未建立或啟動容器。
- 2026-10-03 在 QNAP Container Station 使用已匯入的 AMD64 Production Image 建立一次性 `mmold-hub-uid-check` 診斷容器；建立摘要確認網路模式 `None`、restart policy `無`、沒有 port mapping、互動／TTY 關閉，僅將 `DataVol1/Container/mmold-hub/logs` 綁定至 `/mnt/qnap-logs` 並設為唯讀。命令只執行 `id` 及 `stat`，沒有讀取或寫入 Site、secrets、資料庫或檔案內容。日誌實測 `uid=1000(frappe) gid=1000(frappe)`；掛載目錄回報 `1000:100 777 /mnt/qnap-logs`。依 QNAP 路徑選擇器選取後，Container Station 將主機路徑呈現為 `/Container/mmold-hub/logs`。測試結束後已移除該臨時容器（未勾選刪除匿名儲存空間）；Image 與主機目錄仍保留。這只確認唯讀掛載可見與數字身分，不代表寫入權限或 ACL 已安全驗收。
- 2026-10-08 Browser Use 在 Container Station Images 清單確認 fix46 AMD64 Image 已匯入：`mmold-hub/erpnext:v16.37.0-mmold.6.37.0-pd1.6.7-amd64-zh-twfix46`，短 ID `12a5cf8098af`、2.93 GB、未使用。早期候選 `v16.37.0-mmold.6.37.0-pd1.6.7-amd64`（短 ID `69d1a286c5ef`）保留且未使用；未建立容器。正式 GUI YAML 已存至 NAS，大小 6.46 KB；Container Station 以綠色勾號完成驗證，草稿隨即取消，未建立應用程式或容器。`.env` 不會由 Container Station YAML 驗證器自動載入；正式設定仍只引用唯讀 secret 檔。
- QNAP Control Panel > 權限 > 共用資料夾 > 進階權限顯示「啟動進階資料夾權限」及「啟用 Windows ACL」均未勾選。QNAP 官方說明容器在主機上執行並具有 root 能力，且啟用進階資料夾權限可能影響容器操作（[官方排查指引](https://www.qnap.com/en-us/how-to/tutorial/article/how-to-debug-and-fix-common-container-issues-in-container-station)）；因此目前只記錄 File Station 可見權限，不盲目更改全機設定或猜設數字 UID/GID。
- Container Station 目前有 cloudflare、librechat、paperless-ngx、taiga 四個既有應用程式；未建立或修改任何一個。File Station 顯示 `DataVol1/Container` 根目錄已有 `container-station-data`、`database`、`librechat`、`paperless-ngx`、`stacks` 等內容，因此本案掛載使用獨立 `mmold-hub/` 目錄，未指向共享資料夾根目錄。
- 依使用者要求，已於 2026-10-03 在 Container Station 移除兩個標示為未使用的舊 ERPNext 映像：`mmold-erpnext:16.36-hub-0.2.0-print-1.6.7-pdf-16.3.0-amd64`（ID `56b4fc29db70`）及 `mmold-erpnext:16.36-print-1.6.7-pdf-16.3.0-amd64`（ID `84860f2a6495`）。移除前再次確認兩者未被容器使用，且確認對話框僅列出這兩個映像；沒有選取其他映像或容器。背景工作完成後，映像總量由 `21.29 GB` 降至 `15.4 GB`；映像清單已不再出現上述舊標籤。新版 `mmold-hub/erpnext:v16.37.0-mmold.6.37.0-pd1.6.7-amd64`（ID `69d1a286c5ef`）與獨立 MCP `mmold-erpnext-mcp:3.0.4-amd64`（ID `200f5f286aa9`）仍在清單中。MariaDB 與 Redis 固定版本標籤已匯入，其映像 ID 分別為 `cc7f5fdd7c8f`、`166f6f1437e3`，與現存舊標籤共用內容；未建立或啟動任何容器／服務。此映像移除不等同刪除 QNAP 上的其他檔案或部署資料。
- 儲存池先前顯示約 2.9 TB 可用。2026-10-08 QTS 資源監控即時快照：CPU 平均使用率約 16.3%，記憶體使用 `4.12 / 7.55 GB`（54.5%），閒置約 `1.01 GB`、快取約 `2.41 GB`；介面未顯示 swap 數值，此次未能驗證其餘使用量。新 ERPNext 堆疊尚未實測尖峰需求，8 GB NAS 上部署前需評估對既有服務的記憶體影響。Container Station Image 清單顯示 19 個映像項目被使用，這不是容器數量統計。
- 2026-10-08 File Station 對部署 bind mount 目錄保存 owner-only ACL。MariaDB／Redis 對舊 bind mount 探測回報 `Permission denied`，故改用 named volumes；探測已清理。其後移除舊應用時保留兩個 named volumes，以修正版重建 10 個容器；9 個常駐服務執行中，configurator 已停止。該次檢查時 frontend 回應 Frappe 404；後續即時檢查顯示入口登入頁。Site、備份／還原、TLS 與 volume 重啟持久性均未完成驗收；登入尚未提交。
- QNAP 官方 QNE Network 1.0.x 文件雖不是本案 QTS 文件（[QNAP QNE Network 1.0.x：Container Creation](https://docs.qnap.com/operating-system/qne-network/1.0.x/en-us/container-creation-1A95801A.html)），但本案已直接在目標 Container Station 3.1.2.1742 以正式 GUI Compose 草稿驗證主要語法成功。fix46 Image 已匯入；named volume 建立、容器啟動／重啟及 bind mount 寫入 ACL 仍未驗證。

## 階段狀態與風險

部署範本與容器執行不等於可上線。fix47 已匯入但未使用；9 個常駐服務仍使用 fix46，configurator 已退出。LAN `8088` 正確映射至 frontend 並顯示登入頁，但未登入；正式 Site 目錄空白且存在部分初始化殘留。兩次 bootstrap 都已停止，記錄分別指出 `apps.txt` 遺失及 Chromium lock file 寫入遇到 `Disk quota exceeded`；QTS 顯示 `mmold` 配額尚有約 397.94 GB、DataVol1 尚有約 2.8 TB，因此錯誤不應直接歸因於這兩項容量上限。本機兩份 Compose 未掛載錯誤目標 `frappe-bench/config`，可能是容器可寫層限制，但尚待驗證；部署 README 對 config mount 的描述亦與 Compose 不符。MariaDB 持續記錄 app network 資料庫登入拒絕；backend 有 request timeout、Redis 讀取錯誤及 worker 被 SIGKILL 後重啟的記錄。這些事件的時間脈絡與根因尚待唯讀盤點，登入頁可載入不代表登入、API、佇列或背景工作正常。QTS 進階資料夾權限維持關閉；Site、logs、backups、secrets 仍使用 bind mount。備份目錄目前空白；secret 檔名已存在，但其讀取權限、Site 初始化與資料庫對應、volume 重啟持久性、備份／還原演練及 8 GB NAS 記憶體尖峰影響均未驗收。

資料庫 schema migration 不能單靠降回舊 image 回復；須使用 upgrade 前 database 與 files 備份整組還原。Phase 7 完整登入最後驗收亦仍待使用者提供／輸入隔離測試帳號認證。

`bootstrap_site.py` 為避免密碼進入 CLI process arguments，直接呼叫鎖定 Frappe v16 的 `_new_site` installer API；這是 Frappe private API，未來 Framework 升級前必須重新檢視並在隔離站驗證，禁止無測試沿用。

## 回復

NAS 保留早期 AMD64 候選映像、fix46 與 fix47 映像；fix46 已被重建後的 `mmold-hub` 容器使用，fix47 未使用。MariaDB／Redis named volumes 在移除舊應用及容器時未刪除，並已由新容器重新掛載，目前均顯示「使用中」，必須保留。File Station 原始 Compose、備份及隔離副本均保留；原始 YAML 尚未同步此次修正。正式 Site 目錄空白，另有部分初始化殘留；若日後移除／重建應用程式定義，必須保留 volumes，不得使用刪除儲存空間的選項。

### 2026-10-08 Chromium fix47 後續與服務記錄唯讀檢查

QNAP 配額頁現顯示 `mmold` 500 GB 中已用 102.0595 GB、可用 397.9404 GB；DataVol1 顯示約 2.8 TB 可用。這排除一般使用者 quota 或整體磁碟已滿作為直接原因，但未驗證 Docker writable layer 的配額。Print Designer Chromium setup 回報建立 lock file 時 `Disk quota exceeded`；目標路徑 `/home/frappe/frappe-bench/config` 未在本機兩份 Compose 中設為 bind mount，較可能是容器可寫層或其限制，仍須隔離驗證。部署 README 誤稱 config bind mount 已加入，與實際 Compose 不符；本輪只記錄落差，沒有改 Compose、建立 NAS 目錄或變更 ACL。較早一次 bootstrap log 還顯示 Frappe installer 找不到 `apps.txt`，顯示當時映像／掛載內容也未滿足初始化前提。fix47 已預先提供 PD v1.6.7 所需 Bench 相對路徑並設定 `chromium_binary_path`，映像已匯入但未套用；NAS 現行服務仍使用 fix46。尚未以 QNAP 執行 fix47 Chromium setup 或 PDF 測試。File Station 只讀盤點顯示正式 Site 目錄空白、mount-target 目錄有部分初始化檔案、備份目錄空白；secrets 資料夾已有兩個預期檔案，但存取權限尚未驗證。Container Station 記錄頁另顯示 MariaDB 反覆回報 app network 連線帳號驗證拒絕；backend 記錄顯示 request timeout、Redis socket/read traceback、worker timeout／SIGKILL 與新 worker 啟動。這些是記錄頁的觀察，不足以判定唯一根因，亦未證明資料遺失或 volume 損毀。下一步先做唯讀的 Site／DB 狀態與服務健康盤點；再在獲得明確確認後建立一致性備份，之後才評估 fix47 與 Site 安全修復。不得重跑 bootstrap、刪除／搬移 Site 檔案或重建資料庫。

### 2026-10-09 Container Station volumes 與資源總覽唯讀檢查

Container Station 儲存空間清單即時顯示共 21 個 volume 項目，其中 11 個使用中；`mmold-hub-mariadb` 與 `mmold-hub-redis-queue` 均仍存在、歸屬 `mmold-hub` 且狀態為「使用中」，掛載點位於 Container Station 管理的 local volume 目錄。未開啟 volume 動作選單、未建立／刪除／修改任何 volume。映像清單先前已確認 fix47 為「未使用」、正式常駐容器使用 fix46。Container Station 總覽當下顯示 NAS 總記憶體 7.55 GB、記憶體使用率約 67%；backend 與 MariaDB 分別約占 1.6% 與 1.1%。這是單一時點的觀察，不代表尖峰需求，也不能單獨判定 worker SIGKILL 根因。NAS 備份目錄仍空白，尚未取得使用者對在該目錄建立備份的明確授權，因此未寫入 NAS。
