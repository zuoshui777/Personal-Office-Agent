# Personal Office Agent

基于 **FastAPI、React、LangGraph、MCP、Qdrant、Redis** 的个人 AI
办公助手。

一个支持个人知识管理、项目隔离、RAG 问答、多 Agent
协作和工具调用的智能办公平台。

------------------------------------------------------------------------

# 功能

-   用户注册、登录、JWT 鉴权
-   多项目数据隔离
-   PDF、Word、Excel、TXT、MD、代码上传
-   RAG 知识库问答
-   LangGraph 多 Agent 编排
-   MCP 工具调用
-   长期记忆
-   企业微信通知
-   Redis 上传队列
-   全局搜索
-   通知中心
-   暗色模式

------------------------------------------------------------------------

# 技术栈

## 后端

-   Python 3.11
-   FastAPI
-   SQLAlchemy
-   PostgreSQL
-   Redis
-   Qdrant
-   LangGraph
-   DeepSeek API
-   MCP SDK

## 前端

-   React 18
-   TypeScript
-   Vite
-   Zustand

## 部署

-   Docker
-   Docker Compose
-   Electron

------------------------------------------------------------------------

# 项目结构

``` text
personal-office-agent/
├── backend/                 # FastAPI 后端
│   └── app/
│       ├── api/             # 路由层
│       ├── core/            # 配置、安全、依赖
│       ├── database/        # 数据库连接
│       ├── models/          # ORM 模型
│       ├── schemas/         # Pydantic 模型
│       ├── services/        # 业务逻辑、上传队列、向量检索
│       └── vector_store/    # Qdrant 封装
├── frontend/                # React 前端
│   └── src/
│       ├── pages/           # 页面
│       ├── components/      # 组件
│       ├── layouts/         # 布局
│       ├── hooks/           # 自定义 Hook
│       ├── store/           # Zustand
│       └── services/        # API 封装
├── agent/                   # LangGraph Agent
├── poa_mcp/                 # MCP 工具与官方 MCP Server
├── skills/                  # 项目自身技能
├── embeddings/              # Embedding 封装
├── knowledge_base/          # 知识库处理封装
├── migrations/              # Alembic 迁移
├── scripts/                 # 工具脚本
├── docker/                  # Docker 配置
└── storage/                 # 上传文件和本地配置
```

------------------------------------------------------------------------

# 快速开始

## 创建环境

``` bash
#Conda：
conda create -n poa python=3.11
conda activate poa
#venv（Python 内置，无需额外安装）:
python -m venv venv
source venv/bin/activate
```

安装依赖：

``` bash
pip install -r requirements.txt
```

配置：

``` bash
#Linux/macOS
cp .env.example backend/.env
vim backend/.env
#Windows
copy .env.example backend\.env
notepad backend\.env
# 编辑 ../backend/.env，填入 API Key 等配置
```

初始化数据库：

``` bash
python -m alembic upgrade head
```

启动后端：

``` bash
uvicorn backend.app.main:app --reload
```

启动前端（新开一个终端）：

``` bash
cd frontend
npm install
npm run dev
```

访问：

``` text
http://localhost:5173
```

------------------------------------------------------------------------

# Docker 部署


``` bash
cd docker
docker compose up -d --build
```

查看：

``` bash
docker compose ps
```

停止：

``` bash
docker compose down
```

------------------------------------------------------------------------

# Electron 打包

进入前端：

``` bash
cd frontend
npm install
npm run electron:build:win
```

------------------------------------------------------------------------

# 环境变量

文件：

``` text
backend/.env
```

配置：

``` text
LLM_BASE_URL=https://api.deepseek.com
LLM_API_KEY=
LLM_MODEL=deepseek-v4-flash

JWT_SECRET=

WECHAT_WEBHOOK_URL=

POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=poa
POSTGRES_PASSWORD=poa
POSTGRES_DB=poa

QDRANT_HOST=localhost
QDRANT_PORT=6333

REDIS_HOST=localhost
REDIS_PORT=6379
```

------------------------------------------------------------------------

# 文档

项目说明：

``` text
docs/
├── 项目总结.md
└── Personal_Office_Agent_任务清单与后续优化建议.md
```
