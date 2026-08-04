# Embedding 模型封装

from app.services.embedding import embed_texts


def embed_text(text: str):
    return embed_texts([text])[0]
