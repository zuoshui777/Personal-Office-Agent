# 知识库检索服务

from app.services.embedding import embed_texts
from app.services.vector_store import client, COLLECTION_NAME
from app.services.retriever import build_project_filter


def retrieve_documents(
    query: str,
    limit: int = 5,
    project_id: int | None = None
):

    # 问题转向量
    query_vector = embed_texts(
        [query]
    )[0]


    # Qdrant搜索
    result = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        query_filter=build_project_filter(project_id),
        limit=limit
    )


    documents = []


    for point in result.points:

        documents.append(
            {
                "document_id": point.payload.get(
                    "document_id"
                ),

                "file_name": point.payload.get(
                    "file_name"
                ),

                "text": point.payload.get(
                    "text"
                ),

                "score": point.score
            }
        )


    return documents
