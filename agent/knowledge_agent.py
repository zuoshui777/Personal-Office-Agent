# Knowledge Agent
# 负责 RAG 检索与最终回答

import json
import re

from app.services.retriever import search_documents
from app.services.llm import chat_with_llm
from poa_mcp.hub import execute_tool, list_tools


SYSTEM_PROMPT = """你是一个 Personal Office Agent。
当前推理模型是 DeepSeek V4 Flash，图片识别能力由 MIMO v2.5 提供。
内部由 Knowledge Agent、Browser Agent、Document Agent、Workflow Agent 组成，
由 Router Agent 根据用户任务选择对应 Agent 执行。
回答时：
1. 优先使用知识库资料。
2. 结合长期记忆和聊天历史理解上下文。
3. 如果资料没有答案，可以说明资料中未找到，并使用模型能力给出常识性回答。
4. 如果用户询问你是什么模型，直接说明 DeepSeek V4 Flash 和 MIMO v2.5 的分工。
5. 如果用户询问你有几个 Agent，说明内部有 Knowledge、Browser、Document、Workflow 四个 Agent，由 Router Agent 调度。
6. 不得编造用户未说过的话，不得编造 Webhook、URL、API Key 或配置信息。配置缺失时直接说明“未配置”。"""


def build_system_prompt():
    tools = list_tools()
    tool_text = "\n".join(
        f"- {tool['name']}: {tool['description']} 参数: {tool.get('parameters', [])}"
        for tool in tools
    ) if tools else "暂无可用 MCP 工具"
    return (
        SYSTEM_PROMPT
        + "\n\n可用 MCP 工具：\n"
        + tool_text
        + "\n当用户任务需要工具时，自行选择合适工具执行。"
        + "\n企业微信 Webhook 已保存在设置中。用户要求发送通知时，调用 wechat_notify 只需传 message/text/content，不需要传 webhook_url。只有用户本次提供新地址时才传 webhook_url。"
        + "\n如果需要调用工具，请只输出 JSON：{\"tool\":\"工具名\",\"arguments\":{...}}"
    )


def build_messages(
    question: str,
    context: str,
    history: list,
    memories: list
):
    memory_text = "\n".join(
        f"{item['key']}: {item['value']}"
        for item in memories
    ) if memories else "暂无"

    messages = [{"role": "system", "content": build_system_prompt()}]
    messages.extend(history)
    messages.append(
        {
            "role": "user",
            "content": f"长期记忆：\n{memory_text}\n\n参考资料：\n{context}\n\n当前问题：\n{question}"
        }
    )
    return messages


def run_knowledge_agent(
    question: str,
    project_id: int | None,
    history: list,
    memories: list,
    limit: int = 5
):
    docs = search_documents(question, project_id=project_id, limit=limit)
    context = "\n\n".join(doc["text"] for doc in docs)
    messages = build_messages(question, context, history, memories)
    answer = chat_with_llm(messages)

    match = re.search(r"\{.*\}", answer, re.S)
    if match:
        try:
            tool_call = json.loads(match.group(0))
            tool_name = tool_call.get("tool")
            arguments = tool_call.get("arguments", {})
            available = {item["name"] for item in list_tools()}
            if tool_name in available:
                tool_result = execute_tool(tool_name, arguments)
                messages.append({"role": "assistant", "content": answer})
                messages.append(
                    {
                        "role": "user",
                        "content": f"工具执行结果：\n{tool_result}\n请根据工具结果回答用户问题：{question}"
                    }
                )
                answer = chat_with_llm(messages)
        except Exception as exc:
            messages.append({"role": "assistant", "content": answer})
            messages.append(
                {
                    "role": "user",
                    "content": f"工具调用失败：{exc}\n请不要输出 JSON，直接回答用户问题：{question}"
                }
            )
            answer = chat_with_llm(messages)

    sources = sorted(set(doc["file_name"] for doc in docs))
    return {
        "answer": answer,
        "sources": sources,
        "docs": docs
    }
