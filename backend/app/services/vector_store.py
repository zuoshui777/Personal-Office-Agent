# 向量数据库服务
# 负责创建集合，并保存文本向量

import uuid
import os

from app.core.config import settings
from qdrant_client.models import Filter, FieldCondition, MatchValue
from qdrant_client import QdrantClient
from qdrant_client.models import (
    VectorParams,
    Distance,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue
)

# 本地 Qdrant 不应走系统代理
os.environ.setdefault("NO_PROXY", "localhost,127.0.0.1")
os.environ.setdefault("no_proxy", "localhost,127.0.0.1")


# 连接Qdrant
client = QdrantClient(
    host=settings.QDRANT_HOST,
    port=settings.QDRANT_PORT,
    trust_env=False
)


COLLECTION_NAME = "documents"


# 创建集合
def create_collection():

    # 判断是否存在
    collections = (
        client
        .get_collections()
        .collections
    )

    names = [
        c.name
        for c in collections
    ]


    if COLLECTION_NAME not in names:

        client.create_collection(
            collection_name=COLLECTION_NAME,

            vectors_config=VectorParams(
                size=512,
                distance=Distance.COSINE
            )
        )



# 保存向量
def save_vectors(
    vectors,
    payloads
):

    points = []


    for i, vector in enumerate(vectors):

        points.append(
            PointStruct(

                id=str(uuid.uuid4()),

                vector=vector,

                payload=payloads[i]
            )
        )


    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )
def delete_vectors(document_id: int):

    """
    根据文件名删除Qdrant中的向量
    """

    client.delete(
        collection_name=COLLECTION_NAME,

        points_selector=Filter(

            must=[

                FieldCondition(

                    key="document_id",

                    match=MatchValue(
                        value=document_id
                    )

                )

            ]

        )
    )
