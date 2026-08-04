# Personal Office Agent — 技术设计文档（SDD）

> 版本：v1.0 整合版 · 配套文档：Personal_Office_Agent_PRD_整合版.md

---

## 1 技术栈

| 模块 | 方案 |
|------|------|
| LLM | DeepSeek API |
| Embedding | BGE-M3 |
| Agent 框架 | LangGraph |
| 工具调用协议 | MCP |
| 向量数据库 | Qdrant |
| 关系数据库 | PostgreSQL |
| 缓存 | Redis |
| 浏览器自动化 | Playwright |
| OCR | PaddleOCR |
| 前端 | React + TypeScript + Electron |
| 后端 | FastAPI（Python） |
| 流式输出 | SSE |
| 认证 | JWT |
| 反向代理 | Nginx |
| 部署 | Docker + Linux |

---

## 2 系统总体架构

```
Electron Client (React + TypeScript UI)
        |  SSE
        v
FastAPI API
        |
        v
LangGraph Engine
        |
   +----+----+----+
   v    v    v
Knowledge  Browser  Workflow
  Agent    Agent    Agent
        |
        v
   MCP Hub
   +---+---+---+---+
   v   v   v   v
 File Excel Browser Github
 MCP  MCP  MCP  MCP
        |
   +----+----+----+
   v    v    v
Qdrant  PostgreSQL  Redis
```

---

## 3 核心模块职责

- **Electron（桌面应用层）**：负责桌面应用外壳、文件上传交互、权限弹窗确认、Agent 执行过程实时展示。产品形态对标 ChatGPT Desktop / Claude Desktop。
- **FastAPI（后端服务层）**：提供 RESTful API 与 SSE 流式输出，负责 Agent 调度与请求路由。
- **LangGraph（Agent 引擎层）**：负责状态管理、Agent 编排与工具调用，驱动多 Agent 工作流。

---

## 4 项目目录结构

```
personal-office-agent/
├── frontend/        # React + TypeScript 前端
├── backend/         # FastAPI 后端
├── agent/           # LangGraph Agent 定义
├── mcp/             # MCP 插件服务
├── embeddings/      # Embedding 模型封装
├── knowledge_base/  # 知识库处理（解析/切片/检索）
├── storage/         # 文件存储
├── docker/          # Docker 编排文件
├── scripts/         # 工具脚本
└── docs/            # 项目文档
```

**前端结构**（`frontend/src/`）：`pages/`、`components/`、`layouts/`、`hooks/`、`store/`、`services/`、`types/`

**后端结构**（`backend/app/`）：`api/`、`services/`、`models/`、`schemas/`、`database/`、`vector_store/`、`core/`

---

## 5 Agent 设计

### Router Agent

负责任务分类与意图识别，将用户请求路由到对应 Agent。例如"帮我总结论文"路由到 Document Agent，"查一下最新 YOLO 论文"路由到 Browser Agent。

### Knowledge Agent

负责 RAG 问答。流程：用户问题 → BGE-M3 Embedding → Qdrant 检索 → CrossEncoder 重排序 → DeepSeek 生成答案（附带来源引用）。

### Browser Agent

负责联网搜索与 Playwright 自动化。流程：检测到缺少知识 → 搜索 → 抓取网页内容 → LLM 总结。支持 Google、Bing、GitHub、CSDN、知乎等站点。

### Workflow Agent

负责复杂任务拆解。例如生成答辩 PPT：读取论文 → 生成提纲 → 生成 PPT → 保存文件。

---

## 6 LangGraph 设计

### State 定义

```python
class AgentState(TypedDict):
    user_input: str
    task_type: str
    retrieved_docs: list
    need_web: bool
    tool_result: str
    final_answer: str
```

### 工作流

```
START -> Router -> Knowledge Search -> 判断置信度 -> 是否联网?
  | 是 -> Browser Agent -> Tool Execute -> Answer Generate -> END
  | 否 -> Answer Generate -> END
```

---

## 7 RAG 架构设计

**文档解析**：支持 PDF、DOCX、PPTX、XLSX、TXT、MD、PY、JAVA；图片经 PaddleOCR 转为文本。

**Chunk 切分**：`chunk_size=800`，`chunk_overlap=100`。

**Embedding 模型**：BGE-M3。

**检索流程**：用户问题 → Embedding → Qdrant 检索 TopK=10 → CrossEncoder 重排取 Top3 → DeepSeek 生成答案。

---

## 8 数据存储设计

### 8.1 Qdrant 向量库

**Collection: `document_chunks`**——存储文档切片、OCR 内容与项目说明。

```json
{ "chunk_id": "", "document_id": "", "content": "", "project_name": "", "file_type": "" }
```

**Collection: `memory_collection`**——存储用户长期记忆。

```json
{ "memory_type": "", "content": "" }
```

### 8.2 PostgreSQL 关系库

| 表 | 字段 |
|------|------|
| users | id, username, password_hash, role, created_at |
| projects | id, project_name, description |
| documents | id, project_id, file_name, file_path, file_type, created_at |
| tasks | id, task_name, status, result, created_at |
| memories | id, key, value, source |

### 8.3 Redis 缓存

缓存内容：Agent 状态、SSE 消息队列、用户 Session、权限缓存。

Key 设计示例：`agent:task:{id}`、`user:session:{id}`、`permission:{id}`

---

## 9 MCP 设计

### 协议格式

```json
{ "tool_name": "", "arguments": {} }
```

### 插件清单

| 插件 | 支持操作 |
|------|----------|
| File MCP | 搜索文件、读取文件、创建文件 |
| Browser MCP | 搜索网页、打开网页、自动填写 |
| Excel MCP | 读取 Excel、统计分析、图表生成 |
| GitHub MCP | 分析仓库、生成 README |

未来扩展：企业微信 MCP（消息通知）、邮件插件、数据库插件、天气插件、翻译插件。

---

## 10 权限系统

| 等级 | 名称 | 允许操作 | 说明 |
|------|------|----------|------|
| Level 0 | 只读 | 文件查询、知识库检索 | — |
| Level 1 | 办公 | Word 生成、Excel 生成、PPT 生成 | — |
| Level 2 | 自动化 | 浏览器操作、文件下载 | — |
| Level 3 | 危险 | 删除文件、自动发送消息 | 必须二次确认 |

---

## 11 API 设计

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/chat` | 发送聊天消息 |
| POST | `/api/upload` | 上传文件至知识库 |
| POST | `/api/task` | 创建任务 |
| GET | `/api/task/{id}` | 获取任务状态与结果 |
| GET | `/api/chat/stream` | Agent 流式输出（SSE） |

**SSE 返回格式**：`{ "type": "token", "content": "..." }`

---

## 12 Docker 部署

服务拆分：`frontend`、`backend`、`postgres`、`redis`、`qdrant`。通过 `docker compose up -d` 一键启动。

---

## 13 开发路线

| 阶段 | 内容 |
|------|------|
| 第一阶段 | 知识库搭建：文件上传、多格式解析、BGE-M3 Embedding、Qdrant 存储 |
| 第二阶段 | 聊天能力：DeepSeek 接入、SSE 流式输出、RAG 问答 |
| 第三阶段 | LangGraph：Router Agent、Knowledge Agent、状态机工作流 |
| 第四阶段 | Playwright：Browser Agent 联网搜索与网页自动化 |
| 第五阶段 | MCP 插件：File MCP、Browser MCP 等插件化工具 |

---

## 14 长期记忆系统

系统自动记录用户的专业、项目经历、技术栈、常用目录与常用模板等结构化信息，存入 `memories` 表与 Qdrant `memory_collection` 中。用户在对话中提供个人信息（如"我的专业是人工智能"）时系统自动写入记忆，后续生成简历、报告等场景自动引用，减少重复输入。
