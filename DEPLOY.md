# 部署指南

本系统由 **Vercel (Python Serverless)** 托管核心逻辑，**Notion** 作为数据库与控制台，**Cloudflare Worker** 作为定时触发器。

## 1. Notion 准备

1.  在 Notion 中创建一个新的 **Database**（数据库）。
2.  设置以下属性（字段名需严格一致）：
    *   `Title` (标题, 默认)
    *   `RedditURL` (URL)
    *   `Summary` (Text / Rich Text)
    *   `Scores` (Text / Rich Text) -> 用于存储 JSON 评分
    *   `Category` (Select) -> 选项：AI工具, 自动化, 数据分析, 内容工具, 工具类, 商业工具
    *   `Status` (Status) -> 选项：**待评估** (默认), **开始开发**, **已上线**
    *   `Priority` (Select) -> 选项：HIGH, MEDIUM, LOW
    *   `OnlineURL` (URL)
    *   `RepoURL` (URL)
    *   `Changelog` (Text / Rich Text)
3.  创建一个 **Notion Integration** (在 https://www.notion.so/my-integrations)。
4.  获取 `Internal Integration Secret` (即 `NOTION_API_TOKEN`)。
5.  在数据库页面的右上角 "..." -> "Connections" 中添加刚才创建的 Integration。
6.  获取数据库 ID (`NOTION_DB_ID`)：从 URL 中提取，例如 `notion.so/myworkspace/a8aec43384f447ed84390e8e42c2e089?v=...` 中的 `a8aec43384f447ed84390e8e42c2e089`。

## 2. Vercel 部署 (核心后端)

### 方法 A: 使用 Vercel CLI (推荐)
1.  安装 CLI: `npm i -g vercel`
2.  在项目根目录运行: `vercel`
3.  配置环境变量 (在 Vercel Dashboard 或 CLI 中设置):
    *   `NOTION_API_TOKEN`: (步骤 1.4 获取)
    *   `NOTION_DB_ID`: (步骤 1.6 获取)
    *   `VERCEL_TOKEN`: (可选，用于自动部署子项目，在 Vercel Account Settings -> Tokens 创建)
    *   `VERCEL_PROJECT_ID`: (可选，用于自动部署子项目)

### 方法 B: 连接 Git
1.  将代码推送到 GitHub/GitLab。
2.  在 Vercel Dashboard 中 "Add New Project"。
3.  导入仓库。
4.  在 "Environment Variables" 中添加上述变量。
5.  点击 "Deploy"。

部署成功后，你会获得一个域名，例如 `https://product-auto-builder.vercel.app`。

## 3. Cloudflare CRON 触发器

为了实现定时采集，我们需要一个 Cloudflare Worker 来定期调用 Vercel 的 `/api/collect` 接口。

1.  登录 Cloudflare Dashboard -> Workers & Pages。
2.  点击 "Create Application" -> "Create Worker"。
3.  将 `cloudflare-cron.js` 的内容复制到 Worker 编辑器中。
4.  修改代码中的 `TARGET_URL` 为你的 Vercel 域名 (例如 `https://product-auto-builder.vercel.app/api/collect`)。
5.  保存并部署。
6.  在 Worker 的 "Settings" -> "Triggers" 中，添加 "Cron Triggers"。
7.  设置频率，例如 `*/30 * * * *` (每 30 分钟一次)。

## 4. 验证

1.  **测试采集**: 访问 `https://<your-domain>/api/collect` (POST)，或等待 Cron 触发。检查 Notion 数据库是否出现新条目。
2.  **测试开发流程**: 在 Notion 中将某个条目状态改为 `开始开发`。
3.  **测试 Webhook/轮询**: 访问 `https://<your-domain>/api/notion-webhook` (POST)，应能看到该条目。
