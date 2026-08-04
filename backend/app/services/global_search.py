# 全局搜索
# 搜索当前用户的项目、文档和聊天历史

from sqlalchemy import or_

from app.models.project import Project
from app.models.document import Document
from app.models.chat_session import ChatSession
from app.models.chat_message import ChatMessage


def search_global(
    db,
    user_id: int,
    query: str,
    project_id: int | None = None
):
    """返回项目、文档、聊天三类搜索结果。"""

    q = f"%{query.strip()}%"

    project_query = (
        db.query(Project)
        .filter(Project.user_id == user_id)
    )
    if query.strip():
        project_query = project_query.filter(
            or_(
                Project.project_name.ilike(q),
                Project.description.ilike(q)
            )
        )
    projects = project_query.order_by(Project.created_at.desc()).limit(20).all()

    document_query = (
        db.query(Document)
        .join(Project, Document.project_id == Project.id)
        .filter(Project.user_id == user_id)
    )
    if project_id:
        document_query = document_query.filter(
            Document.project_id == project_id
        )
    if query.strip():
        document_query = document_query.filter(
            or_(
                Document.file_name.ilike(q),
                Document.content.ilike(q)
            )
        )
    documents = document_query.order_by(Document.created_at.desc()).limit(20).all()

    message_sessions = (
        db.query(ChatMessage.session_id)
        .filter(
            ChatMessage.user_id == user_id,
            ChatMessage.content.ilike(q)
        )
        .distinct()
    )
    session_query = (
        db.query(ChatSession)
        .filter(ChatSession.user_id == user_id)
    )
    if project_id:
        session_query = session_query.filter(
            ChatSession.project_id == project_id
        )
    if query.strip():
        session_query = session_query.filter(
            or_(
                ChatSession.title.ilike(q),
                ChatSession.session_id.in_(message_sessions)
            )
        )
    sessions = session_query.order_by(ChatSession.updated_at.desc()).limit(20).all()

    return {
        "projects": [
            {
                "id": item.id,
                "name": item.project_name,
                "description": item.description or ""
            }
            for item in projects
        ],
        "documents": [
            {
                "id": item.id,
                "file_name": item.file_name,
                "file_type": item.file_type or "",
                "created_at": item.created_at
            }
            for item in documents
        ],
        "sessions": [
            {
                "session_id": item.session_id,
                "title": item.title,
                "project_id": item.project_id,
                "updated_at": item.updated_at
            }
            for item in sessions
        ]
    }
