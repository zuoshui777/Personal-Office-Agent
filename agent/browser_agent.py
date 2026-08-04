# Browser Agent
# 使用 Playwright 联网搜索；浏览器不可用时回退到 DuckDuckGo HTML

import urllib.parse
import urllib.request
import re
from datetime import datetime
from zoneinfo import ZoneInfo

from app.services.llm import chat_with_llm


def search_with_playwright(query: str) -> str:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        url = "https://www.bing.com/search?q=" + urllib.parse.quote(query)
        page.goto(url, timeout=20000)
        page.wait_for_timeout(1500)
        text = page.inner_text("body")
        browser.close()
        return text[:6000]


def search_with_duckduckgo(query: str) -> str:
    url = "https://html.duckduckgo.com/html/?q=" + urllib.parse.quote(query)
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0"}
    )
    with urllib.request.urlopen(req, timeout=20) as response:
        html = response.read().decode("utf-8", errors="ignore")
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text)
    return text[:6000]


def search_with_bing(query: str) -> str:
    url = "https://www.bing.com/search?q=" + urllib.parse.quote(query)
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0"}
    )
    with urllib.request.urlopen(req, timeout=20) as response:
        html = response.read().decode("utf-8", errors="ignore")
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text)
    return text[:6000]


def search_web(query: str) -> str:
    for search in (search_with_duckduckgo, search_with_bing):
        try:
            return search(query)
        except Exception:
            continue
    return "联网搜索失败：网络不可达"


def run_browser_agent(
    question: str,
    history: list,
    memories: list
):
    is_time = any(word in question for word in ("几点", "时间", "现在几", "current time"))
    is_date = any(word in question for word in ("今天几号", "今天日期", "日期", "几号", "date"))

    if is_time or is_date:
        now = datetime.now(ZoneInfo("Asia/Shanghai"))
        weekday_map = {
            0: "星期一",
            1: "星期二",
            2: "星期三",
            3: "星期四",
            4: "星期五",
            5: "星期六",
            6: "星期日"
        }
        weekday = weekday_map[now.weekday()]
        if is_time:
            answer = f"当前时间是 {now.strftime('%Y-%m-%d %H:%M:%S')}，{weekday}。"
        else:
            answer = f"今天是 {now.strftime('%Y年%m月%d日')}，{weekday}。"
        return {
            "answer": answer,
            "sources": ["系统时间"],
            "tool_result": answer
        }

    try:
        web_text = search_web(question)
    except Exception as exc:
        web_text = f"联网搜索失败：{exc}"

    memory_text = "\n".join(
        f"{item['key']}: {item['value']}"
        for item in memories
    ) if memories else "暂无"

    messages = [
        {
            "role": "system",
            "content": "你是 Browser Agent，负责联网搜索和实时信息查询。工具已经返回实时结果，直接基于结果回答用户问题，不要说自己无法浏览。"
        },
        *history,
        {
            "role": "user",
            "content": f"长期记忆：\n{memory_text}\n\n联网结果：\n{web_text}\n\n问题：\n{question}"
        }
    ]
    answer = chat_with_llm(messages)
    return {
        "answer": answer,
        "sources": ["联网搜索结果"],
        "tool_result": web_text[:2000]
    }
