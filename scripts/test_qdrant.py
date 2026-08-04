import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__) + "/.."))
# HuggingFace国内镜像加速
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

from app.services.embedding import embed_texts
from app.services.vector_store import create_collection, save_vectors

texts = [
    "这是一个办公文档",
    "这是人工智能知识库"
]

create_collection()
vectors = embed_texts(texts)
save_vectors(
    vectors,
    [{"text": texts[0]}, {"text": texts[1]}]
)
print("向量保存成功")
