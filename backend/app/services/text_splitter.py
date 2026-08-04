# 文本切片模块
# 将长文本切成适合向量检索的小段


def split_text(
    text: str,
    chunk_size: int = 500,
    overlap: int = 50
):

    chunks = []


    start = 0


    text_length = len(text)


    while start < text_length:

        # 当前切片结束位置
        end = start + chunk_size


        chunk = text[start:end]


        chunks.append(chunk)


        # 下一段向前重叠50字符
        start += chunk_size - overlap


    return chunks