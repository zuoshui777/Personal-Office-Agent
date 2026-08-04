# 存储目录自动创建

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]

STORAGE_DIRS = [
    "storage",
    "storage/uploads",
    "storage/outputs",
    "storage/cache"
]


def ensure_storage_dirs():
    for relative in STORAGE_DIRS:
        (PROJECT_ROOT / relative).mkdir(parents=True, exist_ok=True)
