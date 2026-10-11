# 隔離 Frappe Site 安裝測試

此 Compose 供本機 Phase 2–5 隔離驗證使用，不是 Production 架構。僅將 frontend 綁定至主機 `127.0.0.1:8080`，MariaDB、Redis、backend、workers、scheduler 與 websocket 均不直接對外發布，並使用 Compose project `mmold_hub_isolated` 的專屬 volumes。Phase 5 固定納入 Print Designer v1.6.7；一次性 `site-installer` 會連出下載其鎖定版 Chromium，其他服務留在內部網路。PDF on Submit 不安裝、不載入測試映像，也不會自動於文件提交時建立附件。

正式 Secret 不得使用於此環境。執行時透過環境變數提供一次性測試密碼；日常 Phase 2–5 預設映像為 `mmold-hub/erpnext-test:0.4.2`，Phase 7 可將 `MMOLD_TEST_IMAGE` 指向本機 AMD64 Production Image，以重用隔離服務與資料 volumes：

```bash
MMOLD_TEST_DB_ROOT_PASSWORD='<test-only>' \
MMOLD_TEST_ADMIN_PASSWORD='<test-only>' \
docker compose -f tests/isolated-site/compose.yaml up --build \
  -d --wait
```

安裝完成後使用以下 HTTP 網址，不可使用 HTTPS：

```text
http://mmold-test.localhost:8080
```

若瀏覽器啟用「一律使用安全連線」而自動改成 HTTPS，請直接輸入完整的 `http://` 與 `:8080`。此隔離環境未配置 TLS 憑證，使用 `https://mmold-test.localhost` 會得到 `ERR_SSL_PROTOCOL_ERROR`。

安裝結果以 `site-installer` exit code、`list-apps`、runtime compatibility command、Chromium 執行檔、字型清單與登入頁 HTTP 回應為準。環境預設保留，以便後續查驗；需要刪除時必須明確執行：

```bash
docker compose -f tests/isolated-site/compose.yaml down --volumes
```

`down --volumes` 會刪除隔離測試 Site 與資料庫，屬破壞性操作，不應自動執行。
