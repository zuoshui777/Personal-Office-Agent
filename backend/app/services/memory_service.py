# 长期记忆服务

import re

from app.models.memory import Memory


MEMORY_PATTERNS = [
    (r"我的(?:专业|方向)是(.+?)(?:[，。]|$)", "专业"),
    (r"我是(.+?)(?:[，。]|$)", "身份"),
    (r"我(?:做过|参与过|负责过)(.+?)(?:[，。]|$)", "项目经历"),
    (r"我擅长(.+?)(?:[，。]|$)", "技能"),
    (r"我常用(.+?)(?:[，。]|$)", "常用工具"),
    (r"我的(?:常用目录|工作目录)是(.+?)(?:[，。]|$)", "常用目录"),
    (r"我喜欢(.+?)(?:[，。]|$)", "偏好"),
    (r"我使用(.+?)(?:[，。]|$)", "工具"),
    (r"我主要用(.+?)(?:[，。]|$)", "技术栈")
]


def get_memories(db, user_id: int):
    items = (
        db.query(Memory)
        .filter(Memory.user_id == user_id)
        .order_by(Memory.id.desc())
        .all()
    )
    return [
        {
            "id": item.id,
            "key": item.key,
            "value": item.value,
            "source": item.source or ""
        }
        for item in items
    ]


def extract_and_save_memories(db, user_id: int, question: str):
    for pattern, key in MEMORY_PATTERNS:
        match = re.search(pattern, question)
        if not match:
            continue
        value = match.group(1).strip()
        if not value:
            continue
        exists = (
            db.query(Memory)
            .filter(
                Memory.user_id == user_id,
                Memory.key == key
            )
            .first()
        )
        if exists is None:
            db.add(
                Memory(
                    user_id=user_id,
                    key=key,
                    value=value,
                    source="用户输入"
                )
            )
            db.commit()
