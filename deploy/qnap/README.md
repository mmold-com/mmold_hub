# QNAP Container Station 一鍵部署

## 下載 YAML

[下載 Container Station Compose YAML](https://raw.githubusercontent.com/mmold-com/mmold_hub/main/deploy/qnap/compose.container-station.yaml)

Container Station 的「建立應用程式」流程是貼上 Docker Compose YAML；下載上述原始檔後，將全部內容貼入 YAML 欄位，再按「建立」即可。建立時會自動從公開的 GitHub Container Registry 下載 AMD64 映像，啟動 MariaDB、Redis、ERPNext/Frappe、前端、背景工作服務，並執行首次 Site 初始化。QNAP 的建立流程與 YAML 驗證方式請見[官方說明](https://docs.qnap.com/operating-system/qne-network/1.0.x/zh-tw/建立容器-1A95801A.html)。

## 建立前一次性準備

Compose 刻意不把密碼寫在 YAML、GitHub 或容器環境變數中。建立應用程式前，請先確認 NAS 有以下目錄：

- `/share/CACHEDEV1_DATA/Container/mmold-hub/sites`
- `/share/CACHEDEV1_DATA/Container/mmold-hub/logs`
- `/share/CACHEDEV1_DATA/Container/mmold-hub/backups`
- `/share/CACHEDEV1_DATA/Container/mmold-hub/secrets`

在 `secrets` 目錄放置兩個 UTF-8 純文字檔：

- `db_root_password`：MariaDB root 密碼
- `erp_admin_password`：ERPNext Administrator 初始密碼

兩個密碼需自行設定為強密碼；不要貼到聊天、GitHub、YAML 或一般部署日誌。確認 Frappe 執行帳號 UID 1000 可以寫入 `sites`、`logs`、`backups`，Container Station 可唯讀掛載 `secrets`。若任一路徑或檔案不存在，Compose 會停止，不會自動建立空白密碼檔。

## Container Station 操作

1. 在 GitHub 點上方的 YAML 下載連結，下載原始 YAML。
2. QNAP Container Station 選「建立」→「建立應用程式」，輸入應用程式名稱（例如 `mmold-hub`），貼上整份 YAML。
3. 按「驗證 YAML」，確認無錯誤後按「建立」。Container Station 會下載映像並啟動整個服務組。
4. `site-bootstrap` 會自動執行一次，建立 `hub.mmold.com` Site。建立完成後，在區域網路開啟 `http://<QNAP_IP>:8088`。

首次建置會下載約 1 GB 的 ERPNext 映像，所需時間取決於 NAS 與網路速度。資料庫、queue Redis 使用固定名稱的 Container Station local named volume；Site、日誌與備份保存在上列 NAS 資料夾。刪除或重建應用程式時，請勿刪除連接的 named volumes。

## 若首次初始化失敗

檢查 Container Station 中 `site-bootstrap`、`configurator` 與 MariaDB 的日誌。若 `sites/hub.mmold.com` 已存在，初始化程式會拒絕覆寫；先盤點 Site 資料庫與備份，再決定修復方式，不要直接刪除目錄或 named volume 後重跑。

## 映像來源

- GHCR 映像：`ghcr.io/mmold-com/mmold_hub:v16.37.0-fix47`
- GitHub Release（手動匯入映像的替代方式）：[v16.37.0-fix47](https://github.com/mmold-com/mmold_hub/releases/tag/v16.37.0-fix47)
- 容器映像僅支援 `linux/amd64`，適用於 QNAP x86-64 機種。
