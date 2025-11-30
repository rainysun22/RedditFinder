产品需求发现与开发执行系统

后端运行于 Vercel Python Serverless。对外输出为 JSON。

API 路由：
- POST /api/collect
- POST /api/generate
- POST /api/deploy
- POST /api/notion-update

## 部署说明

请查看 [DEPLOY.md](./DEPLOY.md) 获取详细的部署指南，包括 Notion 配置、Vercel 部署和 Cloudflare CRON 设置。
