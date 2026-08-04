# 企业微信 Webhook 设置持久化

import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
WEBHOOK_PATH = PROJECT_ROOT / "storage/wechat_webhook.json"


def _ensure_storage():
    WEBHOOK_PATH.parent.mkdir(parents=True, exist_ok=True)


def get_wechat_webhook() -> str:
    if not WEBHOOK_PATH.exists():
        return ""
    data = json.loads(WEBHOOK_PATH.read_text(encoding="utf-8"))
    return data.get("webhook_url", "")


def save_wechat_webhook(webhook_url: str):
    _ensure_storage()
    WEBHOOK_PATH.write_text(
        json.dumps({"webhook_url": webhook_url}, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def delete_wechat_webhook():
    if WEBHOOK_PATH.exists():
        WEBHOOK_PATH.unlink()
