# 企业微信通知 MCP

import json
import urllib.request

from app.core.config import settings
from app.services.notification_service import notify_user
from app.services.wechat_settings import get_wechat_webhook


def send_notification(
    user_id: int = 0,
    title: str = "",
    content: str = "",
    message: str = "",
    text: str = "",
    webhook_url: str | None = None
):
    if not title:
        title = message or text
    url = webhook_url or get_wechat_webhook() or settings.WECHAT_WEBHOOK_URL
    if not url:
        return {"error": "未配置企业微信 Webhook"}

    payload = {
        "msgtype": "text",
        "text": {
            "content": f"{title}\n{content}"
        }
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=10) as response:
        response.read()

    if user_id and user_id > 0:
        notify_user(user_id, title, content, "info")
    return {"message": "通知已发送"}


def register(register_tool):
    register_tool(
        "wechat_notify",
        "发送企业微信/系统通知，优先使用设置中已保存的 Webhook；参数: user_id, title, content, message, text, webhook_url(可选)",
        send_notification,
        permission="high"
    )
