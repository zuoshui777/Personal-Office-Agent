# 任务管理 API

import threading

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.connection import SessionLocal, get_db
from app.core.dependencies import get_current_user, resolve_project_id
from app.models.task import Task
from app.models.user import User
from app.services.agent_service import run_agent


router = APIRouter(
    prefix="/tasks",
    tags=["任务管理"]
)


class TaskCreate(BaseModel):
    task_name: str
    prompt: str
    project_id: int | None = None


def run_task_in_background(task_id: int, user_id: int, project_id: int | None, prompt: str):
    db = SessionLocal()
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if task is None:
            return
        task.status = "running"
        db.commit()

        result = run_agent(prompt, user_id, db, project_id=project_id)
        task.status = "success"
        task.result = result["answer"]
        db.commit()
    except Exception as exc:
        task = db.query(Task).filter(Task.id == task_id).first()
        if task:
            task.status = "failed"
            task.result = str(exc)
            db.commit()
    finally:
        db.close()


@router.post("/")
def create_task(
    payload: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project_id = resolve_project_id(db, current_user, payload.project_id)
    task = Task(
        user_id=current_user.id,
        project_id=project_id,
        task_name=payload.task_name,
        status="pending",
        result=""
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    thread = threading.Thread(
        target=run_task_in_background,
        args=(task.id, current_user.id, project_id, payload.prompt),
        daemon=True
    )
    thread.start()

    return {
        "id": task.id,
        "task_name": task.task_name,
        "status": task.status
    }


@router.get("/")
def list_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    tasks = (
        db.query(Task)
        .filter(Task.user_id == current_user.id)
        .order_by(Task.id.desc())
        .limit(50)
        .all()
    )
    return [
        {
            "id": item.id,
            "task_name": item.task_name,
            "status": item.status,
            "result": item.result or "",
            "project_id": item.project_id,
            "created_at": item.created_at
        }
        for item in tasks
    ]


@router.get("/{task_id}")
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = (
        db.query(Task)
        .filter(
            Task.id == task_id,
            Task.user_id == current_user.id
        )
        .first()
    )
    if task is None:
        raise HTTPException(404, "任务不存在")
    return {
        "id": task.id,
        "task_name": task.task_name,
        "status": task.status,
        "result": task.result or "",
        "project_id": task.project_id,
        "created_at": task.created_at
    }
