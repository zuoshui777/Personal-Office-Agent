# 系统通知服务
# 将上传、删除、项目变更等状态写入通知表

from app.database.connection import SessionLocal
from app.models.notification import Notification


def notify_user(
    user_id: int,
    title: str,
    content: str = "",
    type: str = "info"
):
    """写入一条用户通知。"""

    db = SessionLocal()
    try:
        db.add(
            Notification(
                user_id=user_id,
                title=title,
                content=content,
                type=type
            )
        )
        db.commit()
    finally:
        db.close()
