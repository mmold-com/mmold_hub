# 09 QNAP Container Station Production Analysis

## 建議架構

使用官方 Frappe Docker Compose 模式：frontend、backend、websocket、queue-short、queue-long、scheduler、configurator，加上 MariaDB、redis-cache、redis-queue；MCP 與 cloudflared 各自獨立 Container。不得合併成單一 Container。

## Network Segmentation

- ingress：cloudflared 只連 frontend 與 MCP。
- app：frontend/backend/websocket/workers/scheduler/MCP。
- data：MariaDB/Redis，只允許必要 app service；不 publish 3306/6379。

## Persistent Storage

MariaDB data、sites、public/private files、backup、必要 logs 與 redis-queue data 要持久化；redis-cache 可重建。QNAP 實際路徑不得猜測，先以 `QNAP_BASE_PATH=` 留白，部署前驗證 UID/GID（Frappe sites 常見 1000、MariaDB/Redis 依映像確認）、ACL、備份帳號與寫入測試。

## 平台風險

先確認 NAS CPU 為 amd64 或 arm64；官方 v16.36.0 兩者皆有 Image，但第三方 App、Chromium、字型與 QNAP Kernel 必須在實機測。Container Station 對 Compose、BuildKit secrets、healthcheck 與 multi-network 的支援需實測。

