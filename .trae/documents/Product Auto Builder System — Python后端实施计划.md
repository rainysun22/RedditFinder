# 概览

* 目标：构建一个可被 Cloudflare CRON 定时触发的全自动系统，完成 Reddit 采集→分析与打分→写入 Notion→等待挑选→自动开发→自动部署→回写 Notion 的全流程。

* 约束：所有对外输出严格 JSON；后端用 Python 实现；默认部署到 Vercel（可选 Cloudflare Pages/Workers 作为前端/触发器）；可拓展处以 JSON 字段保留 `_note` 或 `_ext`。

## 系统架构

* **触发层**：Cloudflare Worker（Scheduled CRON）调用后端 `POST https://<vercel-app>/api/collect`。

* **后端（Python）**：部署在 Vercel Serverless（`api/*.py`）。模块：

  * `collector`：调用 `redditsfinder` 或官方 Reddit API；输出标准 JSON。

  * `analyzer`：规则与轻量模型结合的打分器；输出评分 JSON。

  * `notion_sync`：把分析结果写入 Notion 数据库。

  * `notion_webhook`：通过 Notion 或定时轮询监听选中项（状态变更到“开始开发”）。

  * `generator`：根据选中项生成产品方案与代码库（Next.js 前端 + Python 后端 API）。

  * `deployer`：使用 Vercel REST API 自动部署，返回上线 URL。

  * `notion_update`：把上线信息与 changelog 回写 Notion。

* **前端（模板）**：Next.js（可在生成阶段按需创建）。

* **存储**：无状态优先；去重与状态跟踪放在 Notion；临时缓存用 KV（可选 Redis/Upstash）、或将最小状态嵌入 Notion 属性。

## 环境变量

* `REDDIT_CLIENT_ID`、`REDDIT_CLIENT_SECRET`、`REDDIT_USER_AGENT`

* `REDDITSFINDER_API_KEY`（如使用第三方）

* `NOTION_API_TOKEN`、`NOTION_DB_ID`

* `VERCEL_TOKEN`、`VERCEL_PROJECT_ID`（用于自动部署）

* 可选：`GITHUB_TOKEN`（如需推送 Git 仓库）

## 数据契约（JSON）

### 阶段1：采集输出

```json
{
  "posts": [
    {
      "id": "t3_abcdef",
      "subreddit": "Entrepreneur",
      "title": "...",
      "body": "...",
      "score": 123,
      "num_comments": 45,
      "created_utc": 1732920000,
      "url": "https://reddit.com/r/...",
      "permalink": "/r/.../comments/...",
      "author": "username",
      "_ext": {"source": "redditsfinder"}
    }
  ],
  "count": 120,
  "_note": "收集50-200条，按热度和新鲜度过滤"
}
```

### 阶段2：分析与打分输出

```json
{
  "analysis": [
    {
      "id": "t3_abcdef",
      "title": "...",
      "summary": "需求摘要",
      "scores": {
        "PainScore": 8.2,
        "FeasibleScore": 7.5,
        "MarketSizeScore": 7.9,
        "CompetitionScore": 6.8,
        "OverallScore": 7.6
      },
      "category": "AI工具",
      "recommendation": "HIGH",
      "reddit_url": "https://reddit.com/r/..."
    }
  ],
  "_note": "OverallScore=(Pain+Feasible+MarketSize+Competition)/4"
}
```

### 阶段3：写入 Notion（单条）

```json
{
  "page": {
    "title": "...",
    "reddit_url": "https://reddit.com/r/...",
    "summary": "需求摘要",
    "scores": {
      "PainScore": 8.2,
      "FeasibleScore": 7.5,
      "MarketSizeScore": 7.9,
      "CompetitionScore": 6.8,
      "OverallScore": 7.6
    },
    "category": "AI工具",
    "status": "待评估",
    "priority": "HIGH"
  }
}
```

### 阶段5：自动开发产出（方案与清单）

```json
{
  "design": {
    "feature_desc": ["核心功能1", "核心功能2"],
    "tech_stack": {
      "frontend": "Next.js",
      "backend": "Python (Vercel Serverless)",
      "infra": ["Vercel", "Cloudflare Worker(CRON)"]
    },
    "api": [
      {"method": "GET", "path": "/api/items", "desc": "列表"},
      {"method": "POST", "path": "/api/items", "desc": "创建"}
    ],
    "data_structures": {
      "Item": {"id": "string", "name": "string", "created_at": "number"}
    }
  },
  "repo_manifest": {
    "name": "product-<slug>",
    "files": [
      "README.md",
      "vercel.json",
      "frontend/next.config.js",
      "frontend/app/page.tsx",
      "backend/api/items.py",
      "backend/api/deploy.py"
    ]
  }
}
```

### 阶段6：自动部署产出

```json
{
  "deploy": {
    "platform": "vercel",
    "project_id": "...",
    "url": "https://product-slug.vercel.app",
    "deployment_id": "dpl_...",
    "commit": "<sha>"
  }
}
```

### 阶段7：回写 Notion

```json
{
  "update": {
    "status": "已上线",
    "online_url": "https://product-slug.vercel.app",
    "repo_url": "https://github.com/<org>/<repo>",
    "changelog": ["初始化版本", "修复bug#1"]
  }
}
```

## 打分算法（可迭代）

* `PainScore`：正文关键词强度（如“痛点”“耗时”“昂贵”“手动”），评论量、热度、提问频次、情绪倾向（轻量情感分析）。

* `FeasibleScore`：需求复杂度估计（实体类型数、外部依赖数量、是否需要重度AI）、现成开源或服务可复用度。

* `MarketSizeScore`：子版体量（订阅数）、近7/30天相关帖频次、互动率（score/评论）。

* `CompetitionScore`（反向）：搜索相似产品命中数、GitHub/产品站点数量，命中越多分越低；反向归一化到1-10。

* 所有评分统一到 \[1,10]；`OverallScore` 为简单平均（可加权）。

## 路由与流程

* `POST /api/collect`：采集→分析→写入 Notion→返回两个 JSON（posts 与 analysis 汇总）。

* `POST /api/notion-webhook`：接收 Notion 状态变更（或轮询任务），当 `status==开始开发` 则进入生成。

* `POST /api/generate`：输入选中项 id→生成设计与代码清单→产出压缩包或仓库。

* `POST /api/deploy`：部署到 Vercel→返回 URL。

* `POST /api/notion-update`：把上线信息与 changelog 回写。

## 代码结构（Python 后端）

```json
{
  "backend": {
    "runtime": "python3",
    "modules": [
      "collector.py",
      "analyzer.py",
      "notion_sync.py",
      "webhooks.py",
      "generator/__init__.py",
      "generator/next_template/",
      "deployer.py",
      "logger.py"
    ],
    "entrypoints": {
      "api_collect": "api/collect.py",
      "api_generate": "api/generate.py",
      "api_deploy": "api/deploy.py",
      "api_notion_update": "api/notion_update.py"
    }
  }
}
```

## Notion 数据库字段

* `Title`（标题）

* `RedditURL`（URL）

* `Summary`（摘要）

* `Scores`（JSON 或分列）

* `Category`（选择）

* `Status`（状态：待评估/开始开发/已上线）

* `Priority`（HIGH/MEDIUM/LOW）

* `OnlineURL`、`RepoURL`、`Changelog`（上线后填充）

## 部署策略

* 使用 Vercel REST API：创建或更新项目、上传打包文件（或 Git 推送），触发部署，轮询 deployment 状态，取最终 URL。

* Cloudflare Worker 仅做 CRON 调度与转发，核心逻辑在 Python 后端，满足“后端用 Python 实现”。

## 错误处理与监控

* 全链路请求日志（去除敏感信息）；重试与退避；对 Reddit API 加速与限速；部署失败自动告警（邮件/Webhook）。

## 安全

* 所有密钥仅存环境变量；绝不写入仓库。

## 确认后执行的具体步骤

1. 初始化 Vercel Python Serverless 项目结构与基础路由。
2. 接入 Reddit API/`redditsfinder` 并完成采集器与分页、去重。
3. 实现打分器（规则版），输出标准 JSON。
4. 对接 Notion：数据库建模与写入、状态监听（Webhook/轮询）。
5. 完成代码生成器（Next.js 前端 + Python API 后端模板）。
6. 对接

