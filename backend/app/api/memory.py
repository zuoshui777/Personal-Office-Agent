# 长期记忆接口

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.memory import Memory
from app.services.memory_service import get_memories


router = APIRouter(
    prefix="/memories",
    tags=["长期记忆"]
)


class MemoryCreate(BaseModel):
    key: str
    value: str


@router.get("/")
def list_memories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_memories(db, current_user.id)


@router.post("/")
def create_memory(
    payload: MemoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    memory = Memory(
        user_id=current_user.id,
        key=payload.key,
        value=payload.value,
        source="手动添加"
    )
    db.add(memory)
    db.commit()
    db.refresh(memory)
    return {
        "id": memory.id,
        "key": memory.key,
        "value": memory.value
    }


@router.delete("/{memory_id}")
def delete_memory(
    memory_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    item = (
        db.query(Memory)
        .filter(
            Memory.id == memory_id,
            Memory.user_id == current_user.id
        )
        .first()
    )
    if item is None:
        raise HTTPException(404, "记忆不存在")
    db.delete(item)
    db.commit()
    return {"message": "记忆已删除"}
