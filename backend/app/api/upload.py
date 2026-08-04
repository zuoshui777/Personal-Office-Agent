# 文件上传接口
# 支持 PDF/DOCX/TXT/MD
# 上传后自动解析、切片、Embedding、保存Qdrant


import os
import uuid
import shutil
from pathlib import Path


from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session


from app.database.connection import get_db

from app.core.dependencies import get_current_user

from app.models.user import User

from app.models.project import Project

from app.models.document import Document


from app.services.document_parser import parse_document, SUPPORTED_SUFFIXES

from app.services.upload_queue import enqueue_upload
from app.services.notification_service import notify_user


router = APIRouter(
    prefix="/upload",
    tags=["文件上传"]
)


PROJECT_ROOT = Path(__file__).resolve().parents[3]
UPLOAD_DIR = PROJECT_ROOT / "storage/uploads"


os.makedirs(
    UPLOAD_DIR,
    exist_ok=True
)


SUPPORTED_EXTENSIONS = SUPPORTED_SUFFIXES


@router.post("/")
def upload_file(

    project_id:int,

    file:UploadFile = File(...),

    current_user:User = Depends(get_current_user),

    db:Session = Depends(get_db)

):
    ext = os.path.splitext(
        file.filename
    )[1].lower()

    if ext not in SUPPORTED_EXTENSIONS:

        raise HTTPException(
            400,
            "只支持pdf、docx、txt、md"
        )

    project = db.query(Project).filter(

        Project.id == project_id,

        Project.user_id == current_user.id

    ).first()

    if not project:

        raise HTTPException(
            404,
            "项目不存在"
        )

    # 使用随机文件名保存
    save_name = (
        str(uuid.uuid4())
        +
        ext
    )

    file_path = os.path.join(

        UPLOAD_DIR,

        save_name

    )

    try:
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

        # 保存文件
        with open(
            file_path,
            "wb"
        ) as buffer:

            shutil.copyfileobj(
                file.file,
                buffer
            )

        enqueue_upload(
            project_id=project_id,
            file_path=file_path,
            file_name=file.filename,
            file_type=file.content_type or "",
            user_id=current_user.id
        )


        return {

            "message":"上传已加入队列",
            "queued": True,
            "file_name":file.filename,

        }



    except Exception as e:

        notify_user(
            current_user.id,
            "文件上传失败",
            str(e),
            "error"
        )

        if os.path.exists(file_path):

            os.remove(file_path)



        raise HTTPException(

            500,

            str(e)

        )
