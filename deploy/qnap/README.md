# QNAP Container Station 部署範本

此範本供 Phase 8 使用。QNAP TS-464 `192.168.1.110`、Container Station `3.1.2.1742` 已確認。fix47 AMD64 映像已匯入但尚未套用；目前 9 個常駐服務仍使用 fix46。MariaDB／Redis 固定名稱 local named volumes `mmold-hub-mariadb`、`mmold-hub-redis-queue` 均使用中，不得刪除。frontend 使用 LAN 入口 `0.0.0.0:8088`；未設定路由器轉埠、Internet 公開或 TLS。2026-10-08 只讀檢查顯示正式 Site 子目錄空白、mount-target 目錄有部分初始化檔案，`backups/` 空白；`secrets/` 有兩個預期檔案但權限未驗證。不得重跑 bootstrap、搬移或清除 Site 資料。先完成唯讀資料庫盤點與可還原備份，才能規劃修復。

fix47 的 Dockerfile 會將 `/home/frappe/frappe-bench/chromium/chrome-linux/headless_shell` 預先連結至映像內 Chromium；這是 Print Designer 安裝鉤子實際檢查的位置。Compose 另設定 `chromium_binary_path`，供 PDF 產生器直接執行系統 Chromium。請勿再使用不受此版本程式讀取的 `chromium_path`。

目前 NAS 上的 bootstrap-v6 未完成：Print Designer 的 `after_install` 在建立 `frappe-bench/config/print_designer_chromium_setup.lock` 時回報 `Disk quota exceeded`，未輸出 Site 建立成功訊息。DataVol1 雖有約 2.8 TB 可用空間，仍不能據此排除 Container Station 容器可寫層／配額問題。Site 目錄與資料庫可能已有部分內容，**不可直接重跑 bootstrap 或清除資料**；須先唯讀盤點兩者狀態。

目前兩份 Compose 範本尚未把 `frappe-bench/config` 掛載至 QNAP；Container Station 記錄指出 Print Designer 鎖定檔於此路徑建立時遇到 `Disk quota exceeded`。QTS 配額頁顯示 `mmold` 尚有約 397.94 GB、DataVol1 尚有約 2.8 TB，故需另查 Container Station 容器可寫層或該路徑的限制。可評估新增專用 config bind mount 作為部署層修正，但須先經使用者確認，再建立 NAS 資料夾、核實 frappe UID 1000 的最小必要寫入權限並在隔離環境驗證；不可使用 `chmod 777` 或更動父層 ACL。目前尚未實作或在 NAS 驗證此修正。

## 儲存方式

- MariaDB 與 queue Redis 使用 Container Station 管理的固定名稱 local named volume，避免 QNAP 子資料夾 ACL 與容器 UID/GID 不相容。此設定不啟用 QTS 進階資料夾權限，也不改動 `mariadb/`、`redis-queue/`、`secrets/`、`sites/` 或父目錄 ACL。
- Named volume 會跨容器重建保留資料；移除 Container Station 應用時，不得勾選刪除連接的自訂／匿名儲存空間，也不得使用 `docker compose down --volumes`。建立前應在 Container Station 儲存空間確認兩個 volume 名稱及容量。
- Site、logs、backups 在 `DataVol1/Container/mmold-hub/` 使用 bind mount；目前 Compose **沒有**將 `frappe-bench/config` 掛載至 NAS，該項仍是待確認的修正方案。正式資料庫備份使用 Frappe `bench backup --with-files` 寫入 `backups/`，並依備份文件加密及另存；還原至空白 named volume 時必須先啟動 MariaDB、再匯入備份與 Site 檔案。

## 固定映像

- 範本固定 AMD64 平台與 MariaDB／Redis amd64 manifest；目前 Compose 目標標籤為待建置／封裝的 fix47 Image。匯入 NAS 前須核對映像完整標籤及平台；frontend 預設綁定 `0.0.0.0:8088`，供 NAS 區域網路存取並避開 QTS 管理介面 `8080`；未設定路由器轉埠、Internet 公開或 TLS。
- Site、logs、backups、secrets 目錄 ACL 已逐一核實保存；MariaDB／Redis 已改採 named volume，不需授予 QTS 使用者或群組額外存取權。`secrets/` 內兩個預期檔案已存在，仍須驗證權限與 Container Station 唯讀讀取能力；另須評估 NAS swap／可用記憶體並確認正式 Compose。`config/` 尚未建立或掛載。Site 與資料庫尚未完成安全備份／還原前，不替換現行服務或執行初始化。
- 沒有 `build:`、浮動 `latest`、PDF on Submit 或公開資料庫／快取連接埠。

## 部署前必要條件

1. 正式 GUI 範本已在本機執行 `config --quiet`，並於 QNAP QTS `5.2.10.3577`、Container Station `3.1.2.1742` 的建立應用程式草稿以綠色勾號驗證成功。修正版亦已於 NAS GUI 通過驗證、重建 `mmold-hub` 並啟動長期服務；兩個既有 named volumes 均保留並重新掛載。
2. 使用者指定 `DataVol1/Container`；NAS 實體路徑為 `/share/CACHEDEV1_DATA/Container`。Site、logs、backups、secrets 採 bind mount；目前 Compose 未掛載 `config/`。MariaDB/Redis 使用 Container Station local named volume；必須先驗證其建立與備份／還原方式。不要將 MariaDB 資料目錄放在 SMB/NFS 外掛掛載。
3. 禁止使用 `chmod 777` 或猜設 owner/group。QTS 進階資料夾權限維持關閉；不得修改 parent share 或目錄 ACL。隔離 UID/GID 測試容器已移除。
4. NAS 現有 9 個常駐服務使用 fix46；fix47 已匯入但未使用。更新前須先完成唯讀資料盤點並建立、驗證備份；不得刪除 MariaDB／Redis named volumes。只讀檢查確認正式 Site 子目錄空白，部分初始化檔案另在 `hub.mmold.com.mount-target-20261008`；`backups/` 空白、secrets 檔名存在。禁止直接重跑 bootstrap。
5. 複製本資料夾到 NAS 專用部署目錄，將 `.env.example` 複製為不納入 Git 的 `.env`；只有在 NAS 核實實際掛載路徑並確認專屬目錄為空／可用後，才填入 `QNAP_BASE_PATH`。
6. File Station 已顯示 `${QNAP_BASE_PATH}/secrets/` 內有 `db_root_password` 與 `erp_admin_password` 檔案；不讀取或傳送其內容。部署前驗證檔案權限、UTF-8 格式與容器唯讀讀取能力；禁止放進 `.env`、Compose、映像、日誌或未加密備份副本。
7. Site、logs、backups、secrets 使用的 bind mount 路徑必須存在。若核准新增 `config/` bind mount，需先於 File Station 建立目錄並核實 frappe UID 1000 可寫；不得使用 `chmod 777` 或更動父層／全機 ACL。MariaDB／Redis named volume 由 Container Station 管理；確認重建／刪除應用時不會連帶刪除。
8. 執行 `docker compose --env-file .env config --quiet`，先人工檢查解析後設定中沒有密碼值；此指令只驗證設定，不啟動容器。

## 啟動及初始化

首次初始化會建立資料庫與全新的 Frappe Site，具不可忽略的資料寫入效果。完成備份政策、路徑、ACL、Site 名稱及一次性密碼核對後，才由管理者在 NAS 執行：

```sh
docker compose --env-file .env up -d
docker compose --env-file .env --profile bootstrap run --rm site-bootstrap
```

`site-bootstrap` 只建立新的 `SITE_NAME`，如同名目錄已存在即停止，不會覆寫。密碼只從唯讀掛載的 secret files 讀取，不經 Compose environment 或命令列。初始化完成後應確認一次性服務已退出；不要重複執行在已建立 Site 上。**目前 QNAP 有未完成初始化，禁止依本段直接重跑 bootstrap。**

frontend 發布 `${HTTP_PORT:-8088}:8080` 至 NAS 網卡，預設可由區域網路以 `http://192.168.1.110:8088` 存取。這不會自動開啟路由器轉埠；不得將此 HTTP LAN 入口當成 Internet/TLS 部署。正式網域、HTTPS 與 Cloudflare Tunnel 仍留待 Phase 9 獨立設定與驗收。

## 常用操作

```sh
# 狀態與服務日誌
docker compose --env-file .env ps
docker compose --env-file .env logs --tail=100 backend frontend

# 手動備份（需先驗證目的目錄 ACL 與剩餘空間）
docker compose --env-file .env exec backend \
  bench --site "$SITE_NAME" backup --with-files \
  --backup-path /home/frappe/frappe-bench/backup

# 版本更新前：先完整備份，再載入新映像；migration 僅手動執行
docker compose --env-file .env exec backend \
  bench --site "$SITE_NAME" migrate
```

不要對正式 Site 使用 `down --volumes`。資料庫遷移不是通用降版；版本回復需搭配升級前一致性備份與原映像，並先在隔離副本演練。

## UID/GID 診斷與 ACL 狀態

2026-10-08 隔離建立兩個無網路的 BusyBox 探測容器，以 MariaDB／Redis UID/GID `999:999` 寫入兩個空 bind mount 目錄均回報 `Permission denied`。探測應用程式與容器已移除，Container Station 應用程式數量回到原本 4 個。使用者拒絕啟用全域進階資料夾權限，故正式 Compose 已改用 Container Station local named volume；目前仍待 NAS 驗證 named volume 建立、持久性及備份／還原。

## 尚未驗收

- Container Station named volume 重啟後持久性、備份目的地及快照政策。
- `DataVol1/Container/mmold-hub/compose.container-station.yaml` 已存入 NAS，File Station 顯示 6.46 KB；Container Station 已驗證此 named-volume 版本的 YAML。錯誤雙份檔已改名隔離為 `compose.container-station.duplicate-20261008.yaml`，原始檔另保留備份，兩者勿用於部署。`.env` 不會被 Container Station YAML 驗證器自動載入。僅確認 secret 檔名存在，未讀取內容；勿將密碼傳入聊天或寫入 Git。
- 8088 曾顯示繁體中文登入頁，但不能視為初始化成功或 Site 可登入。bootstrap-v6 已停止，需先確認既有 Site 目錄及 MariaDB 狀態；此步未完成前不重跑初始化。
- 2026-10-08 bootstrap-v6 容器因 Print Designer Chromium setup 的鎖定檔建立錯誤 `Disk quota exceeded` 停止；容器與 named volumes 保留。QTS 配額頁顯示 `mmold` 有 397.94 GB 可用、DataVol1 約有 2.8 TB 可用；兩份 Compose 目前都沒有 config bind mount。config bind mount 僅為待確認／待測的修正方案，未實作、未上傳、未驗證或套用至 QNAP。
- NAS 上 MariaDB／Site 部分初始化盤點、config bind mount 寫入測試、容器可寫層配額原因、Site 安全恢復方式、重啟後資料持續性與還原演練。
- NAS Kernel／Chromium PDF、繁中字型、列印與長時間運轉。
- Cloudflare Tunnel、DNS、HTTPS 與正式流量（Phase 9）。
