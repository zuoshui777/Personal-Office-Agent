# 知识库搜索接口


from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.search_documents import retrieve_documents
from app.services.global_search import search_global


router = APIRouter(
    prefix="/search",
    tags=["知识库搜索"]
)


class RAGSearchRequest(BaseModel):
    query: str
    project_id: int | None = None


@router.post("/")
def search(
    request: RAGSearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    results = retrieve_documents(
        request.query,
        project_id=request.project_id
    )


    return {
        "query":request.query,
        "results":results
    }


@router.get("/global")
def global_search(
    q: str,
    project_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return search_global(
        db,
        current_user.id,
        q,
        project_id
    )
