# 知识库检索服务
# 根据用户问题，从Qdrant中检索相关文档


from app.services.embedding import embed_texts
from app.services.vector_store import client, COLLECTION_NAME
from qdrant_client.models import Filter, FieldCondition, MatchValue


def build_project_filter(project_id):
    if project_id is None:
        return None
    return Filter(
        must=[
            FieldCondition(
                key="project_id",
                match=MatchValue(value=project_id)
            )
        ]
    )


def search_documents(
    query: str,
    limit: int = 5,
    project_id: int | None = None
):
    """
    根据问题搜索知识库

    返回:
    [
        {
            "document_id": 1,
            "file_name": "xxx.pdf",
            "text": "内容",
            "score": 0.8
        }
    ]
    """


    # 1. 问题转向量

    query_vector = embed_texts(
        [query]
    )[0]


    # 2. Qdrant搜索

    result = client.query_points(

        collection_name=COLLECTION_NAME,

        query=query_vector,

        query_filter=build_project_filter(project_id),

        limit=limit,

        with_payload=True

    )


    documents = []


    # 3. 整理结果

    for point in result.points:


        # 过滤低相关内容
        if point.score < 0.25:
            continue


        documents.append(

            {

                "document_id":
                    point.payload.get(
                        "document_id"
                    ),


                "file_name":
                    point.payload.get(
                        "file_name"
                    ),


                "text":
                    point.payload.get(
                        "text"
                    ),


                "score":
                    point.score

            }

        )


    return documents
