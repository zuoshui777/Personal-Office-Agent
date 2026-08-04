# FastAPI 应用入口文件
# 负责创建 FastAPI 应用实例、注册路由、配置 CORS 与中间件
# 启动时初始化数据库连接、Qdrant 连接与 Embedding 模型

from fastapi import FastAPI
from app.core.config import settings
from app.api.auth import router as auth_router
from app.api.upload import router as upload_router
from app.api.chat_history import router as chat_history_router
from fastapi.openapi.utils import get_openapi
from app.api.search import router as search_router
from app.api.chat import router as chat_router
from app.api.notifications import router as notifications_router
from app.api.settings import router as settings_router
from app.api.tools import router as tools_router
from app.api.memory import router as memory_router
from app.api.task import router as task_router
from app.api.sync import router as sync_router
from fastapi.middleware.cors import CORSMiddleware

# 导入项目接口
from app.api.project import router as project_router
from app.api.document import router as document_router
from app.services.runtime_settings import load_runtime_settings
from app.services.upload_queue import start_upload_worker
from app.services.storage import ensure_storage_dirs
from poa_mcp.hub import register_all

ensure_storage_dirs()
register_all()

load_runtime_settings()
start_upload_worker()

app = FastAPI(
    title="Personal Office Agent",
    description="私人办公智能体后端服务",
    version="0.1.0"
)

app.add_middleware(

    CORSMiddleware,

    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174"
    ],

    allow_credentials=True,

    allow_methods=[
        "*"
    ],

    allow_headers=[
        "*"
    ]

)


# 注册用户接口
app.include_router(auth_router)


# 注册项目管理接口
app.include_router(project_router)


# 打印当前所有接口，检查用户接口是否注册成功
for route in app.routes:
    if hasattr(route, "path"):
        print(route.path)


# 注册文件上传接口
app.include_router(upload_router)


#注册大模型借口
app.include_router(chat_router)

#注册历史会话接口
app.include_router(
    chat_history_router
)

# 注册文件管理接口
app.include_router(document_router)

# 注册搜索测试接口
app.include_router(
    search_router
)

app.include_router(notifications_router)
app.include_router(settings_router)
app.include_router(tools_router)
app.include_router(memory_router)
app.include_router(task_router)
app.include_router(sync_router)

# 测试接口
# 用于验证 FastAPI 环境是否正常
@app.get("/")
def root():

    return {
        "message": "Hello from POA",
        "project": settings.PROJECT_NAME
    }

# 通过 uvicorn 启动 FastAPI 服务
if __name__ == "__main__":

    import uvicorn


    # 启动提示
    print("=" * 50)
    print("Personal Office Agent 后端启动成功")
    print("浏览器访问地址:")
    print("http://127.0.0.1:8000")
    print("接口文档地址:")
    print("http://127.0.0.1:8000/docs")
    print("=" * 50)


    # 启动FastAPI服务
    uvicorn.run(
        app,

        # 监听所有网络
        host="0.0.0.0",

        # 服务端口
        port=8000
    )
