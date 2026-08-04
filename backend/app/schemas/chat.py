# 聊天相关的 Pydantic 请求/响应模型
# 定义 ChatRequest（用户消息）、ChatResponse（AI 回复）等结构
# 聊天请求和响应的数据模型



from pydantic import BaseModel
from typing import Optional


# 用户发送的问题
class ChatRequest(BaseModel):

    # 用户问题
    question: str

    # 当前项目
    project_id: Optional[int] = None

    # 会话ID
    # 第一次聊天为空
    # 后续聊天带回来
    session_id: Optional[str] = None



# 聊天响应
class ChatResponse(BaseModel):

    question: str

    answer: str

    sources: list[str]

    session_id: str
