# 测试Embedding模型

import os
import sys
# 将项目根目录加入环境变量
sys.path.append(os.path.abspath(os.path.dirname(__file__) + "/.."))

os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

from app.services.embedding import embed_texts

texts = [
    "这是一个测试文档",
    "人工智能知识库"
]

vectors = embed_texts(texts)

print("向量数量:", len(vectors))
print("向量维度:", len(vectors[0]))



texts = [
    "这是一个测试文档",
    "人工智能知识库"
]


vectors = embed_texts(
    texts
)


print(
    "向量数量:",
    len(vectors)
)


print(
    "向量维度:",
    len(vectors[0])
)