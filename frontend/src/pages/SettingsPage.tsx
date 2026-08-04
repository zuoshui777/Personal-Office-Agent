import { useEffect, useState } from "react"

import {
    createMemory,
    deleteMemory,
    deleteWeChatWebhook,
    getMemories,
    getSettings,
    getWeChatWebhook,
    saveWeChatWebhook,
    testWeChatWebhook
} from "../services/api"
import { useAppStore } from "../store"


export default function SettingsPage() {
    const user = useAppStore((state) => state.user)
    const [llmBaseUrl, setLlmBaseUrl] = useState("")
    const [llmModel, setLlmModel] = useState("")
    const [hasApiKey, setHasApiKey] = useState(false)
    const [memories, setMemories] = useState<any[]>([])
    const [memoryKey, setMemoryKey] = useState("")
    const [memoryValue, setMemoryValue] = useState("")
    const [wechatWebhook, setWechatWebhook] = useState("")
    const [wechatMessage, setWechatMessage] = useState("")

    const loadMemories = () => {
        getMemories()
            .then(setMemories)
            .catch(() => setMemories([]))
    }

    useEffect(() => {
        getSettings()
            .then((data) => {
                setLlmBaseUrl(data.llm_base_url || "")
                setLlmModel(data.llm_model || "")
                setHasApiKey(Boolean(data.llm_api_key))
            })
            .catch(() => undefined)
        loadMemories()
        getWeChatWebhook()
            .then((data) => setWechatWebhook(data.webhook_url || ""))
            .catch(() => undefined)
    }, [])

    const handleSaveWechat = async () => {
        if (!wechatWebhook.trim()) {
            setWechatMessage("请输入企业微信 Webhook 地址")
            return
        }
        try {
            await saveWeChatWebhook(wechatWebhook.trim())
            setWechatMessage("企业微信 Webhook 已保存")
        } catch (error: any) {
            setWechatMessage(error.message || "保存失败")
        }
    }

    const handleTestWechat = async () => {
        try {
            await testWeChatWebhook(wechatWebhook.trim() || undefined)
            setWechatMessage("测试通知已发送")
        } catch (error: any) {
            setWechatMessage(error.message || "测试失败")
        }
    }

    const handleDeleteWechat = async () => {
        try {
            await deleteWeChatWebhook()
            setWechatWebhook("")
            setWechatMessage("企业微信 Webhook 已删除")
        } catch (error: any) {
            setWechatMessage(error.message || "删除失败")
        }
    }

    const handleAddMemory = async () => {
        if (!memoryKey.trim() || !memoryValue.trim()) {
            return
        }
        try {
            await createMemory(memoryKey.trim(), memoryValue.trim())
            setMemoryKey("")
            setMemoryValue("")
            loadMemories()
        } catch {
            // ignore
        }
    }

    const handleDeleteMemory = async (id: number) => {
        try {
            await deleteMemory(id)
            loadMemories()
        } catch {
            // ignore
        }
    }

    const handleLogout = () => {
        localStorage.removeItem("token")
        localStorage.removeItem("currentProjectId")
        window.location.href = "/"
    }

    return (
        <div className="page-panel">
            <div className="page-panel-head">
                <div>
                    <h2>设置</h2>
                    <p>用户信息、长期记忆与只读模型配置</p>
                </div>
            </div>

            <section className="settings-section">
                <h3>用户信息</h3>
                <div className="settings-row">
                    <span>用户名</span>
                    <strong>{user?.username || "-"}</strong>
                </div>
                <div className="settings-row">
                    <span>角色</span>
                    <strong>{user?.role || "-"}</strong>
                </div>
                <button type="button" className="danger-button" onClick={handleLogout}>
                    退出登录
                </button>
            </section>

            <section className="settings-section">
                <h3>模型 API 配置</h3>
                <div className="settings-row">
                    <span>Base URL</span>
                    <strong>{llmBaseUrl || "-"}</strong>
                </div>
                <div className="settings-row">
                    <span>模型名称</span>
                    <strong>{llmModel || "-"}</strong>
                </div>
                <div className="settings-row">
                    <span>API Key</span>
                    <strong>{hasApiKey ? "已配置（不可修改）" : "未配置"}</strong>
                </div>
            </section>

            <section className="settings-section">
                <h3>企业微信接入</h3>
                <input
                    className="text-input"
                    value={wechatWebhook}
                    onChange={(event) => setWechatWebhook(event.target.value)}
                    placeholder="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=..."
                />
                <div className="project-card-actions">
                    <button type="button" className="primary-button" onClick={handleSaveWechat}>
                        保存
                    </button>
                    <button type="button" className="primary-button" onClick={handleTestWechat}>
                        测试通知
                    </button>
                    <button type="button" className="danger-button" onClick={handleDeleteWechat}>
                        删除
                    </button>
                </div>
                {wechatMessage && <div className="form-message">{wechatMessage}</div>}
            </section>

            <section className="settings-section">
                <h3>长期记忆</h3>
                <div className="form-grid">
                    <input
                        className="text-input"
                        value={memoryKey}
                        onChange={(event) => setMemoryKey(event.target.value)}
                        placeholder="记忆类型，如：专业"
                    />
                    <input
                        className="text-input"
                        value={memoryValue}
                        onChange={(event) => setMemoryValue(event.target.value)}
                        placeholder="记忆内容"
                    />
                    <button type="button" className="primary-button" onClick={handleAddMemory}>
                        添加
                    </button>
                </div>
                <div className="tool-list">
                    {memories.map((memory) => (
                        <div className="management-item" key={memory.id}>
                            <div>
                                <strong>{memory.key}</strong>
                                <p>{memory.value}</p>
                            </div>
                            <button
                                type="button"
                                onClick={() => handleDeleteMemory(memory.id)}
                            >
                                删除
                            </button>
                        </div>
                    ))}
                    {memories.length === 0 && <div className="empty-state">暂无长期记忆</div>}
                </div>
            </section>
        </div>
    )
}
