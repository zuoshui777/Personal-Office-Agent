# 聊天历史服务
# 根据session_id读取历史聊天记录


from app.models.chat_message import ChatMessage


def get_chat_history(
    db,
    session_id: str,
    limit: int = 10
):

    """
    获取最近聊天记录

    参数:
        db:
            数据库连接

        session_id:
            会话ID

        limit:
            获取多少条


    返回:
        messages列表
    """


    messages = (
        db.query(ChatMessage)
        .filter(
            ChatMessage.session_id == session_id
        )
        .order_by(
            ChatMessage.created_at.asc()
        )
        .limit(limit)
        .all()
    )


    return [
        {
            "role": message.role,

            "content": message.content
        }

        for message in messages
    ]