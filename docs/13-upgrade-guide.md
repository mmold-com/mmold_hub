# 13 Upgrade Guide

本專案核心已依使用者確認調整為官方 ERPNext v16.37.0，配對官方映像內實際附帶的 Frappe v16.36.0；Custom App 為 6.37.0。後續 v16.x 升級仍須先建立完整備份，在隔離 clone 更新 tag/digest，檢查 Frappe/ERPNext API 與 hooks，安裝 Print Designer，執行 migrate、translation/branding/URL/print/MCP regression 與 restore drill，核准後才部署。PDF on Submit 已移除，不屬於安裝清單。

主要 Upgrade Risks：DOM selector 與 Desk 改版、translation msgid 變動、Print Designer override、MCP protocol/auth 版本、Python/Node/MariaDB/Redis 基線、Chromium rendering 差異。PDF on Submit 移除後，不再有自動提交 PDF 附件功能；若未來重新評估，須另立變更與安全驗收。任何需要 Core patch 的升級都應停止並重新評估擴充點。

Rollback 使用升級前 Image Digest + App Commit + database/files backup；不可只切回 Container Image 而沿用已被新 migration 變更的 DB。
