# 文档管理接口
# 查看、删除用户上传的知识库文件


import os

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session


from app.database.connection import get_db
from app.models.document import Document
from app.models.project import Project
from app.models.user import User

from app.core.dependencies import get_current_user
from app.services.vector_store import delete_vectors
from app.services.notification_service import notify_user

router = APIRouter(

    prefix="/documents",

    tags=["文档管理"]

)


# 查看当前用户文件

@router.get("/")
def get_documents(

    project_id: int,

    category: str | None = None,

    sort: str = "created_at",

    order: str = "desc",

    current_user: User = Depends(get_current_user),

    db: Session = Depends(get_db)

):

    # 检查项目权限

    project = db.query(Project).filter(

        Project.id == project_id,

        Project.user_id == current_user.id

    ).first()

    if project is None:

        raise HTTPException(

            status_code=404,

            detail="项目不存在"

        )

    # 查询文件

    documents = db.query(Document).filter(

        Document.project_id == project_id

    ).all()


    def category_for_file(file_name: str) -> str:
        suffix = os.path.splitext(file_name)[1].lower()
        if suffix in {".pdf", ".docx", ".txt", ".md", ".pptx"}:
            return "document"
        if suffix in {".xlsx", ".csv"}:
            return "sheet"
        if suffix in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp"}:
            return "image"
        if suffix in {".py", ".java", ".js", ".ts", ".json"}:
            return "code"
        return "other"

    items = [
        {
            "id": document.id,
            "file_name": document.file_name,
            "file_path": document.file_path,
            "file_type": document.file_type or "",
            "category": category_for_file(document.file_name),
            "file_size": (
                os.path.getsize(document.file_path)
                if os.path.exists(document.file_path)
                else 0
            ),
            "created_at": document.created_at
        }
        for document in documents
    ]

    if category:
        items = [item for item in items if item["category"] == category]

    reverse = order.lower() == "desc"
    if sort == "file_name":
        items.sort(key=lambda item: item["file_name"].lower(), reverse=reverse)
    elif sort == "file_size":
        items.sort(key=lambda item: item["file_size"], reverse=reverse)
    else:
        items.sort(key=lambda item: item["created_at"], reverse=reverse)

    return items


@router.get("/stats")
def get_document_stats(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()
    if project is None:
        raise HTTPException(404, "项目不存在")

    documents = db.query(Document).filter(
        Document.project_id == project_id
    ).all()

    total_size = sum(
        os.path.getsize(document.file_path)
        for document in documents
        if os.path.exists(document.file_path)
    )
    capacity = 10 * 1024 * 1024 * 1024
    return {
        "total_files": len(documents),
        "used_bytes": total_size,
        "used_display": f"{total_size / 1024 / 1024 / 1024:.2f} GB",
        "capacity_bytes": capacity,
        "capacity_display": "10 GB",
        "percent": min(100, round(total_size / capacity * 100, 1))
    }


# 删除文件

@router.delete("/{document_id}")

def delete_document(

    document_id:int,

    current_user: User = Depends(get_current_user),

    db: Session = Depends(get_db)

):

    # 查询文件

    document = db.query(Document).filter(

        Document.id == document_id

    ).first()

    if document is None:

        raise HTTPException(

            status_code=404,

            detail="文件不存在"

        )

    # 检查所属项目

    project = db.query(Project).filter(

        Project.id == document.project_id,

        Project.user_id == current_user.id

    ).first()


    if project is None:

        raise HTTPException(

            status_code=403,

            detail="无权限删除"

        )

    # 删除本地文件

    if os.path.exists(document.file_path):

        os.remove(document.file_path)

    # 删除数据库记录

    # 删除Qdrant向量
    delete_vectors(
        document.id
    )

    db.delete(document)

    db.commit()

    notify_user(
        current_user.id,
        "文件删除成功",
        document.file_name,
        "success"
    )

    return {

        "message":"文件删除成功",

        "file_name":document.file_name

    }
