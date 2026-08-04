# 大模型服务
# 根据知识库内容生成最终回答

# 大模型服务
# 支持多轮聊天


import os

import httpx
from openai import OpenAI

from app.core.config import settings


def chat_with_llm(
    messages: list
):

    """
    调用大模型

    参数:
        messages:
            OpenAI标准消息格式

    返回:
        AI回答
    """

    os.environ.pop("ALL_PROXY", None)
    os.environ.pop("all_proxy", None)

    print("正在调用 DeepSeek...")

    client = OpenAI(
        api_key=settings.LLM_API_KEY,
        base_url=settings.LLM_BASE_URL,
        http_client=httpx.Client(trust_env=True)
    )

    response = client.chat.completions.create(

        model=settings.LLM_MODEL,

        messages=messages,

        temperature=0.2

    )

    print("DeepSeek 调用完成")

    return response.choices[0].message.content
