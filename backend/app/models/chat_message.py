# 聊天历史数据库模型
# 保存用户和AI的对话记录


from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from app.database.connection import Base


class ChatMessage(Base):

    __tablename__ = "chat_messages"


    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # 用户ID
    user_id = Column(
        Integer,
        nullable=False
    )

    # 一次聊天会话ID
    session_id = Column(
        String(64),
        nullable=False
    )

    # user / assistant
    role = Column(
        String(20),
        nullable=False
    )

    # 消息内容
    content = Column(
        Text,
        nullable=False
    )

    # 创建时间
    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )