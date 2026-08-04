# 测试知识库搜索

import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__) + "/.."))
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
from app.services.retriever import search_documents



result = search_documents(
    "这个文档讲了什么?"
)


for i,text in enumerate(result):

    print(
        "第",
        i,
        "段:"
    )

    print(text)

    print("----------------")