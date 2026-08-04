# 系统通知表
# 保存用户上传、删除、项目变更等操作状态

from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean

from app.database.connection import Base


class Notification(Base):

    __tablename__ = "notifications"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        nullable=False,
        index=True
    )

    title = Column(
        String(100),
        nullable=False
    )

    content = Column(
        Text,
        nullable=True
    )

    type = Column(
        String(30),
        default="info"
    )

    is_read = Column(
        Boolean,
        default=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )
