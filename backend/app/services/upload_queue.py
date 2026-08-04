# Redis / 内存回退的文档上传后台队列

import json
import os
import queue
import threading

import redis

from app.core.config import settings
from app.database.connection import SessionLocal
from app.models.document import Document
from app.services.document_parser import parse_document
from app.services.text_splitter import split_text
from app.services.embedding import embed_texts
from app.services.vector_store import (
    create_collection,
    delete_vectors,
    save_vectors
)
from app.services.notification_service import notify_user


QUEUE_KEY = "poa:uploads"
_memory_queue: queue.Queue = queue.Queue()
_worker_started = False


def _get_redis():
    return redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        decode_responses=True,
        socket_connect_timeout=2
    )


def enqueue_upload(
    project_id: int,
    file_path: str,
    file_name: str,
    file_type: str,
    user_id: int
):
    task = {
        "project_id": project_id,
        "file_path": file_path,
        "file_name": file_name,
        "file_type": file_type,
        "user_id": user_id
    }
    try:
        _get_redis().rpush(QUEUE_KEY, json.dumps(task, ensure_ascii=False))
    except Exception:
        _memory_queue.put(task)


def process_upload(task: dict):
    db = SessionLocal()
    document = None
    try:
        content = parse_document(task["file_path"])
        chunks = split_text(content)
        vectors = embed_texts(chunks)
        create_collection()

        document = Document(
            project_id=task["project_id"],
            file_name=task["file_name"],
            file_path=task["file_path"],
            file_type=task.get("file_type", ""),
            content=content
        )
        db.add(document)
        db.flush()

        save_vectors(
            vectors,
            [
                {
                    "document_id": document.id,
                    "project_id": task["project_id"],
                    "file_name": task["file_name"],
                    "text": chunk
                }
                for chunk in chunks
            ]
        )
        db.commit()
        notify_user(
            task["user_id"],
            "文件上传成功",
            task["file_name"],
            "success"
        )
    except Exception as exc:
        db.rollback()
        if document is not None:
            try:
                delete_vectors(document.id)
            except Exception:
                pass
        if os.path.exists(task["file_path"]):
            os.remove(task["file_path"])
        notify_user(
            task["user_id"],
            "文件上传失败",
            str(exc),
            "error"
        )
    finally:
        db.close()


def _worker_loop():
    while True:
        task_json = None
        try:
            item = _get_redis().blpop(QUEUE_KEY, timeout=1)
            if item:
                task_json = item[1]
        except Exception:
            try:
                task_json = _memory_queue.get(timeout=1)
            except queue.Empty:
                pass

        if task_json:
            try:
                process_upload(json.loads(task_json))
            except Exception:
                pass


def start_upload_worker():
    global _worker_started
    if _worker_started:
        return
    _worker_started = True
    thread = threading.Thread(target=_worker_loop, daemon=True)
    thread.start()
