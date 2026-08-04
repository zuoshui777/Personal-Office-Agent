# 文件夹同步接口

import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.core.dependencies import get_current_user, get_user_project_or_404
from app.models.document import Document
from app.models.user import User
from app.services.document_parser import parse_document, SUPPORTED_SUFFIXES
from app.services.text_splitter import split_text
from app.services.embedding import embed_texts
from app.services.vector_store import create_collection, save_vectors
from app.services.notification_service import notify_user


router = APIRouter(
    prefix="/sync",
    tags=["文件夹同步"]
)


class SyncFolderRequest(BaseModel):
    folder_path: str
    project_id: int


@router.post("/folder")
def sync_folder(
    payload: SyncFolderRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    project = get_user_project_or_404(
        db,
        current_user,
        payload.project_id
    )

    folder = Path(payload.folder_path)
    if not folder.is_dir():
        raise HTTPException(400, "文件夹路径不存在")

    files = [
        file for file in folder.rglob("*")
        if file.is_file() and file.suffix.lower() in SUPPORTED_SUFFIXES
    ]

    indexed = 0
    errors = []
    for file in files:
        existing = (
            db.query(Document)
            .filter(
                Document.project_id == project.id,
                Document.file_name == file.name
            )
            .first()
        )
        if existing:
            continue

        try:
            content = parse_document(str(file))
            document = Document(
                project_id=project.id,
                file_name=file.name,
                file_path=str(file),
                file_type=file.suffix.lower().lstrip("."),
                content=content
            )
            db.add(document)
            db.commit()
            db.refresh(document)

            chunks = split_text(content)
            vectors = embed_texts(chunks)
            create_collection()
            save_vectors(
                vectors,
                [
                    {
                        "document_id": document.id,
                        "project_id": project.id,
                        "file_name": file.name,
                        "text": chunk
                    }
                    for chunk in chunks
                ]
            )
            indexed += 1
        except Exception as exc:
            errors.append({"file": file.name, "error": str(exc)})

    notify_user(
        current_user.id,
        "文件夹同步完成",
        f"发现 {len(files)} 个文件，已索引 {indexed} 个",
        "success"
    )

    return {
        "found": len(files),
        "indexed": indexed,
        "errors": errors
    }
