# 用户设置与模型 API 配置

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.core.config import settings
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.runtime_settings import save_runtime_settings
from app.services.wechat_settings import (
    delete_wechat_webhook,
    get_wechat_webhook,
    save_wechat_webhook
)
from poa_mcp.wechat_mcp import send_notification


router = APIRouter(
    prefix="/settings",
    tags=["设置"]
)


class SettingsUpdate(BaseModel):
    llm_base_url: str
    llm_api_key: str
    llm_model: str


class WeChatWebhookUpdate(BaseModel):
    webhook_url: str


@router.get("/")
def get_settings(
    current_user: User = Depends(get_current_user)
):
    return {
        "username": current_user.username,
        "role": current_user.role,
        "llm_base_url": settings.LLM_BASE_URL,
        "llm_model": settings.LLM_MODEL,
        "llm_api_key": settings.LLM_API_KEY
    }


@router.put("/")
def update_settings(
    payload: SettingsUpdate,
    current_user: User = Depends(get_current_user)
):
    save_runtime_settings(
        payload.llm_base_url.strip(),
        payload.llm_api_key.strip(),
        payload.llm_model.strip()
    )
    return {
        "message": "设置已保存",
        "llm_base_url": settings.LLM_BASE_URL,
        "llm_model": settings.LLM_MODEL
    }


@router.get("/wechat")
def get_wechat(
    current_user: User = Depends(get_current_user)
):
    return {
        "webhook_url": get_wechat_webhook()
    }


@router.put("/wechat")
def update_wechat(
    payload: WeChatWebhookUpdate,
    current_user: User = Depends(get_current_user)
):
    webhook_url = payload.webhook_url.strip()
    save_wechat_webhook(webhook_url)
    return {
        "message": "企业微信 Webhook 已保存",
        "webhook_url": webhook_url
    }


@router.delete("/wechat")
def delete_wechat(
    current_user: User = Depends(get_current_user)
):
    delete_wechat_webhook()
    return {"message": "企业微信 Webhook 已删除"}


@router.post("/wechat/test")
def test_wechat(
    payload: WeChatWebhookUpdate,
    current_user: User = Depends(get_current_user)
):
    webhook_url = payload.webhook_url.strip() or get_wechat_webhook()
    if not webhook_url:
        raise HTTPException(400, "请先填写企业微信 Webhook 地址")

    try:
        send_notification(
            user_id=current_user.id,
            message="Personal Office Agent 企业微信配置测试",
            webhook_url=webhook_url
        )
    except Exception as exc:
        raise HTTPException(400, str(exc))

    return {"message": "测试通知已发送"}
