# 运行时模型配置
# 允许设置页修改 LLM API Key、Base URL 和模型，并持久化到本地文件

import json
from pathlib import Path

from app.core.config import settings


PROJECT_ROOT = Path(__file__).resolve().parents[3]
SETTINGS_PATH = PROJECT_ROOT / "storage/settings.json"


def _ensure_storage():
    SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)


def load_runtime_settings():
    """应用启动时读取本地运行时配置。"""

    _ensure_storage()
    if not SETTINGS_PATH.exists():
        return

    data = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
    settings.LLM_BASE_URL = data.get("llm_base_url", settings.LLM_BASE_URL)
    settings.LLM_API_KEY = data.get("llm_api_key", settings.LLM_API_KEY)
    settings.LLM_MODEL = data.get("llm_model", settings.LLM_MODEL)


def save_runtime_settings(
    llm_base_url: str,
    llm_api_key: str,
    llm_model: str
):
    """保存设置页修改后的模型配置。"""

    _ensure_storage()
    data = {
        "llm_base_url": llm_base_url,
        "llm_api_key": llm_api_key,
        "llm_model": llm_model
    }
    SETTINGS_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    settings.LLM_BASE_URL = llm_base_url
    settings.LLM_API_KEY = llm_api_key
    settings.LLM_MODEL = llm_model
