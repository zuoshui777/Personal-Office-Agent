# 工具中心
# 提供知识库检索、MIMO 图片识别等工具接口

import subprocess
import sys
import json
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.search_documents import retrieve_documents
from poa_mcp.hub import (
    execute_tool as execute_mcp_tool,
    list_tools as list_mcp_tools,
    set_enabled as set_mcp_enabled
)


router = APIRouter(
    prefix="/tools",
    tags=["工具中心"]
)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
MIMO_SCRIPT = Path.home() / "plugins/mimo-vision/scripts/describe_image.py"
SUPPORTED_IMAGE_SUFFIXES = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".bmp",
    ".tiff",
    ".heic"
}


class MimoRequest(BaseModel):
    image_path: str
    prompt: str = "请完整识别并描述这张图片，包括所有可见文字、图表、UI、物体、布局和上下文。"
    project_id: int | None = None


class RagRequest(BaseModel):
    query: str
    project_id: int | None = None


class ToolExecuteRequest(BaseModel):
    name: str
    arguments: dict = {}


class ToggleRequest(BaseModel):
    enabled: bool


AGENT_DEFINITIONS = [
    {
        "name": "knowledge_agent",
        "label": "Knowledge Agent",
        "description": "RAG 知识检索与模型回答"
    },
    {
        "name": "browser_agent",
        "label": "Browser Agent",
        "description": "Playwright 联网搜索与网页读取"
    },
    {
        "name": "document_agent",
        "label": "Document Agent",
        "description": "生成 Word / Excel / PPT"
    },
    {
        "name": "workflow_agent",
        "label": "Workflow Agent",
        "description": "多步骤 Agent 任务编排"
    },
    {
        "name": "mcp_hub",
        "label": "MCP Hub",
        "description": "MCP 工具注册与调用"
    }
]

AGENT_SETTINGS_PATH = PROJECT_ROOT / "storage/agent_settings.json"


def list_agents():
    settings = {}
    if AGENT_SETTINGS_PATH.exists():
        settings = json.loads(AGENT_SETTINGS_PATH.read_text(encoding="utf-8"))
    return [
        {
            **agent,
            "enabled": settings.get(agent["name"], True)
        }
        for agent in AGENT_DEFINITIONS
    ]


def save_agent_enabled(name: str, enabled: bool):
    if name not in {agent["name"] for agent in AGENT_DEFINITIONS}:
        raise HTTPException(404, "Agent 不存在")
    settings = {}
    if AGENT_SETTINGS_PATH.exists():
        settings = json.loads(AGENT_SETTINGS_PATH.read_text(encoding="utf-8"))
    settings[name] = enabled
    AGENT_SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    AGENT_SETTINGS_PATH.write_text(
        json.dumps(settings, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def list_skills():
    roots = [PROJECT_ROOT / "skills"]
    results = []
    for root in roots:
        if not root.exists():
            continue
        for skill_file in root.rglob("SKILL.md"):
            text = skill_file.read_text(encoding="utf-8", errors="ignore")[:2000]
            name = skill_file.parent.name
            description = ""
            for line in text.splitlines():
                if line.startswith("description:"):
                    description = line.split(":", 1)[1].strip()
                    break
            results.append({
                "name": name,
                "description": description,
                "path": str(skill_file)
            })
    return sorted(results, key=lambda item: item["name"])


@router.get("/")
def list_tools():
    return {
        "tools": [
            {
                "id": "rag-search",
                "name": "知识库检索",
                "description": "基于当前项目进行向量检索"
            },
            {
                "id": "mimo-vision",
                "name": "MIMO 图片识别",
                "description": "调用 MIMO v2.5 识别本地图片"
            }
        ],
        "mcp": list_mcp_tools(),
        "agents": list_agents(),
        "skills": list_skills()
    }


@router.get("/mcp")
def get_mcp_tools():
    return {"tools": list_mcp_tools()}


@router.post("/mcp/{name}/toggle")
def toggle_mcp_tool(
    name: str,
    payload: ToggleRequest
):
    try:
        set_mcp_enabled(name, payload.enabled)
    except KeyError:
        raise HTTPException(404, "MCP 工具不存在")
    return {"name": name, "enabled": payload.enabled}


@router.post("/mcp/execute")
def execute_mcp(
    request: ToolExecuteRequest,
    current_user: User = Depends(get_current_user)
):
    try:
        result = execute_mcp_tool(request.name, request.arguments)
    except ValueError as exc:
        raise HTTPException(404, str(exc))
    except PermissionError as exc:
        raise HTTPException(403, str(exc))
    except Exception as exc:
        raise HTTPException(500, str(exc))
    return {"result": result}


@router.get("/agents")
def get_agents():
    return {"agents": list_agents()}


@router.post("/agents/{name}/toggle")
def toggle_agent(
    name: str,
    payload: ToggleRequest
):
    save_agent_enabled(name, payload.enabled)
    return {"name": name, "enabled": payload.enabled}


@router.get("/skills")
def get_skills():
    return {"skills": list_skills()}


@router.post("/rag")
def rag_search(
    request: RagRequest,
    current_user: User = Depends(get_current_user)
):
    results = retrieve_documents(
        request.query,
        project_id=request.project_id
    )
    return {
        "query": request.query,
        "results": results
    }


@router.post("/mimo")
def run_mimo(
    request: MimoRequest,
    current_user: User = Depends(get_current_user)
):
    image_path = Path(request.image_path)
    if not image_path.is_file():
        raise HTTPException(404, "图片路径不存在")

    suffix = image_path.suffix.lower()
    if suffix not in SUPPORTED_IMAGE_SUFFIXES:
        raise HTTPException(400, f"不支持图片格式: {suffix}")

    if not MIMO_SCRIPT.is_file():
        raise HTTPException(500, "MIMO Vision 插件未安装")

    command = [
        sys.executable,
        str(MIMO_SCRIPT),
        str(image_path),
        "--prompt",
        request.prompt
    ]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=180
        )
    except subprocess.TimeoutExpired:
        raise HTTPException(504, "MIMO 识别超时")

    if result.returncode != 0:
        raise HTTPException(
            502,
            result.stderr.strip() or "MIMO 识别失败"
        )

    return {
        "content": result.stdout.strip()
    }
