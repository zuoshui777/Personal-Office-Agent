# 创建项目和查询用户自己的项目

import os

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.project import Project
from app.models.document import Document
from app.models.user import User
from app.core.dependencies import get_current_user
from app.services.vector_store import delete_vectors
from app.services.notification_service import notify_user


# 创建项目接口路由
router = APIRouter(
    prefix="/projects",
    tags=["项目管理"]
)


class ProjectCreate(BaseModel):
    project_name: str
    description: str = ""


# 创建项目
@router.post("/")
def create_project(
    payload: ProjectCreate,

    # 获取当前登录用户
    current_user: User = Depends(get_current_user),

    # 获取数据库
    db: Session = Depends(get_db)
):

    # 创建项目
    project = Project(
        user_id=current_user.id,
        project_name=payload.project_name,
        description=payload.description
    )


    # 保存数据库
    db.add(project)

    db.commit()

    db.refresh(project)

    notify_user(
        current_user.id,
        "项目创建成功",
        project.project_name,
        "success"
    )

    return {
        "message": "项目创建成功",
        "project_id": project.id,
        "project_name": project.project_name,
        "description": project.description or ""
    }



# 查询当前用户的项目
@router.get("/")
def get_projects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    # 查询用户自己的项目
    projects = (
        db.query(Project)
        .filter(
            Project.user_id == current_user.id
        )
        .all()
    )

    project_ids = [project.id for project in projects]
    document_counts = dict(
        db.query(
            Document.project_id,
            func.count(Document.id)
        )
        .filter(Document.project_id.in_(project_ids))
        .group_by(Document.project_id)
        .all()
    ) if project_ids else {}

    return [
        {
            "id": project.id,
            "project_name": project.project_name,
            "description": project.description or "",
            "document_count": document_counts.get(project.id, 0),
            "created_at": project.created_at
        }
        for project in projects
    ]


@router.delete("/{project_id}")
def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    project = (
        db.query(Project)
        .filter(
            Project.id == project_id,
            Project.user_id == current_user.id
        )
        .first()
    )

    if project is None:
        raise HTTPException(404, "项目不存在")

    documents = (
        db.query(Document)
        .filter(Document.project_id == project_id)
        .all()
    )

    for document in documents:
        if os.path.exists(document.file_path):
            os.remove(document.file_path)
        delete_vectors(document.id)
        db.delete(document)

    db.delete(project)
    db.commit()

    notify_user(
        current_user.id,
        "项目已删除",
        project.project_name,
        "warning"
    )

    return {"message": "项目删除成功"}
