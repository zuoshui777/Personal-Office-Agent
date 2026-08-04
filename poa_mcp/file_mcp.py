# File MCP

import os
from pathlib import Path


def search_files(
    path: str = "",
    directory: str = "",
    keyword: str = "",
    pattern: str = "",
    query: str = ""
):
    root = Path(path or directory)
    if not root.exists():
        return {"error": "目录不存在"}
    keyword = keyword or pattern or query
    if keyword.endswith("*"):
        keyword = keyword[:-1]
    results = []
    for file in root.rglob("*"):
        if file.is_file() and (not keyword or keyword.lower() in file.name.lower()):
            results.append(str(file))
            if len(results) >= 50:
                break
    return {"files": results}


def read_file(path: str):
    file = Path(path)
    if not file.is_file():
        return {"error": "文件不存在"}
    return {"content": file.read_text(encoding="utf-8", errors="ignore")[:20000]}


def create_file(path: str, content: str):
    file = Path(path)
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text(content, encoding="utf-8")
    return {"path": str(file)}


def register(register_tool):
    register_tool("file_search", "搜索目录中的文件", search_files)
    register_tool("file_read", "读取本地文件内容", read_file)
    register_tool("file_create", "创建本地文件", create_file, permission="write")
