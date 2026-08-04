# 聊天会话模型
# 保存一次完整聊天的信息


from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

from app.database.connection import Base


class ChatSession(Base):

    __tablename__ = "chat_sessions"


    id = Column(
        Integer,
        primary_key=True,
        index=True
    )


    # UUID，会话唯一标识
    session_id = Column(
        String(64),
        unique=True,
        nullable=False,
        index=True
    )


    # 用户ID
    user_id = Column(
        Integer,
        nullable=False,
        index=True
    )

    # 所属项目ID
    project_id = Column(
        Integer,
        nullable=True,
        index=True
    )


    # 会话标题
    title = Column(
        String(255),
        nullable=False
    )


    # 创建时间
    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


    # 更新时间
    updated_at = Column(
        DateTime,
        default=datetime.utcnow
    )
