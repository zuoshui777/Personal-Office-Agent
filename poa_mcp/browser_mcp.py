# Browser MCP

import re
import urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo

from agent.browser_agent import search_web


def web_search(query: str):
    if any(word in query for word in ("今天几号", "今天日期", "日期", "几号", "date")):
        now_text = datetime.now(ZoneInfo("Asia/Shanghai")).strftime(
            "%Y年%m月%d日 %A"
        )
        return {"content": f"当前日期：{now_text}"}
    try:
        text = search_web(query)
    except Exception as exc:
        text = f"联网搜索失败：{exc}"
    return {"content": text}


def open_page(url: str):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=20) as response:
            html = response.read().decode("utf-8", errors="ignore")
        text = re.sub(r"<[^>]+>", " ", html)
        text = re.sub(r"\s+", " ", text)
        return {"content": text[:10000]}
    except Exception as exc:
        return {"error": str(exc)}


def register(register_tool):
    register_tool("browser_search", "搜索网页内容", web_search)
    register_tool("browser_open", "打开网页并提取正文", open_page, permission="automation")
