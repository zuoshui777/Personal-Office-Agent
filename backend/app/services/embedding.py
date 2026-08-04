# Embedding模型服务
# 负责把文本转换成向量
# 使用懒加载，避免每次启动都等待模型加载

import os
# 设置 HuggingFace国内镜像
# 必须在加载FlagModel之前设置
from dotenv import load_dotenv
load_dotenv()
os.environ.pop("ALL_PROXY", None)
os.environ.pop("all_proxy", None)
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
os.environ["HF_ENDPOINT"] = os.getenv(
    "HF_ENDPOINT",
    "https://hf-mirror.com"
)



# 全局模型变量
model = None


def get_model():

    """
    获取Embedding模型

    第一次调用时加载
    后续直接使用
    """

    global model

    if model is None:

        print("正在加载Embedding模型...")

        from FlagEmbedding import FlagModel
        model = FlagModel(
            "BAAI/bge-small-zh-v1.5",

            # CPU运行
            use_fp16=False
        )

        print("Embedding模型加载完成")


    return model

# 文本转向量

def embed_texts(
    texts: list[str]
):

    """
    输入:
        文本列表

    返回:
        向量列表
    """

    model = get_model()

    embeddings = model.encode(
        texts
    )

    return embeddings.tolist()
