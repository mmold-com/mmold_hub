# 14 Troubleshooting

| 症狀 | 優先檢查 | 禁止捷徑 |
|---|---|---|
| Desk 502/504 | frontend/backend health、Host header、worker、DB/Redis | 不直接暴露 backend |
| Queue 堆積 | redis-queue、worker queue、timeout、job exception | 不刪 queue 當修復 |
| PDF 口口口 | Noto CJK TC、Chromium font cache、實際 CSS font | 不用圖片取代所有文字 |
| PDF submit 慢 | Chromium、同步 hook、格式複雜度、worker 設計 | 不關閉 validation |
| MCP 400 | protocol 2026-07-28 headers/meta | 不當成 OAuth 失敗 |
| MCP 401 | resource metadata、issuer/audience/scope/JWKS | 不取消 authentication |
| Translation 未生效 | locale、MO build、cache、msgid/context | 不改上游 zh_CN |
| QNAP permission denied | UID/GID、shared folder ACL、bind mount | 不用 `chmod 777` |
| Tunnel 可連但登入錯誤 | Host/site mapping、proxy headers、OAuth callback | 不公開內部 ports |

