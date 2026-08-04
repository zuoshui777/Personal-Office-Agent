# 系统通知接口

import asyncio
import json

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.core.dependencies import get_current_user
from app.models.notification import Notification
from app.models.user import User


router = APIRouter(
    prefix="/notifications",
    tags=["系统通知"]
)


def notification_dict(item: Notification) -> dict:
    created_at = item.created_at.isoformat() if item.created_at else None
    return {
        "id": item.id,
        "title": item.title,
        "content": item.content or "",
        "type": item.type,
        "is_read": item.is_read,
        "created_at": created_at
    }


@router.get("/")
def get_notifications(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    items = (
        db.query(Notification)
        .filter(Notification.user_id == current_user.id)
        .order_by(Notification.id.desc())
        .limit(limit)
        .all()
    )
    return [notification_dict(item) for item in items]


@router.post("/read-all")
def mark_all_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    (
        db.query(Notification)
        .filter(
            Notification.user_id == current_user.id,
            Notification.is_read.is_(False)
        )
        .update({"is_read": True})
    )
    db.commit()
    return {"message": "全部已读"}


@router.post("/{notification_id}/read")
def mark_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    item = (
        db.query(Notification)
        .filter(
            Notification.id == notification_id,
            Notification.user_id == current_user.id
        )
        .first()
    )
    if item:
        item.is_read = True
        db.commit()
    return {"message": "已读"}


@router.get("/stream")
def stream_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    async def event_generator():
        last_id = 0
        while True:
            items = (
                db.query(Notification)
                .filter(
                    Notification.user_id == current_user.id,
                    Notification.id > last_id
                )
                .order_by(Notification.id.asc())
                .all()
            )
            if items:
                last_id = max(item.id for item in items)
                yield (
                    "data: "
                    + json.dumps(
                        {
                            "items": [
                                notification_dict(item)
                                for item in items
                            ]
                        },
                        ensure_ascii=False
                    )
                    + "\n\n"
                )
            await asyncio.sleep(2)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )
