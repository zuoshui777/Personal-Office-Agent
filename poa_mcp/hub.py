# MCP Hub
# 统一注册和调用文件、浏览器、Excel、GitHub、通知等工具

import json
import inspect
from pathlib import Path
from typing import Any, Callable


TOOLS: dict[str, dict[str, Any]] = {}
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SETTINGS_PATH = PROJECT_ROOT / "storage/tool_settings.json"


def register_tool(
    name: str,
    description: str,
    handler: Callable[..., Any],
    permission: str = "read"
):
    TOOLS[name] = {
        "name": name,
        "description": description,
        "handler": handler,
        "permission": permission,
        "enabled": True,
        "parameters": list(inspect.signature(handler).parameters.keys())
    }


def list_tools():
    load_settings()
    return [
        {
            "name": item["name"],
            "description": item["description"],
            "permission": item["permission"],
            "enabled": item["enabled"],
            "parameters": item["parameters"]
        }
        for item in TOOLS.values()
    ]


def execute_tool(name: str, arguments: dict[str, Any]):
    load_settings()
    tool = TOOLS.get(name)
    if tool is None:
        raise ValueError(f"未知工具: {name}")
    if not tool["enabled"]:
        raise PermissionError(f"工具已禁用: {name}")
    valid_args = {
        key: value
        for key, value in arguments.items()
        if key in tool["parameters"]
    }
    return tool["handler"](**valid_args)


def register_all():
    load_settings()
    from poa_mcp import file_mcp, browser_mcp, excel_mcp, github_mcp, wechat_mcp

    for module in (
        file_mcp,
        browser_mcp,
        excel_mcp,
        github_mcp,
        wechat_mcp
    ):
        module.register(register_tool)


def load_settings():
    if not SETTINGS_PATH.exists():
        return
    data = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
    for name, enabled in data.items():
        if name in TOOLS:
            TOOLS[name]["enabled"] = bool(enabled)


def save_settings():
    SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    SETTINGS_PATH.write_text(
        json.dumps(
            {name: item["enabled"] for name, item in TOOLS.items()},
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )


def set_enabled(name: str, enabled: bool):
    load_settings()
    if name not in TOOLS:
        raise KeyError(f"未知工具: {name}")
    TOOLS[name]["enabled"] = enabled
    save_settings()
