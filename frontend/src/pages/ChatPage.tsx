import { useEffect, useRef, useState } from "react"

import ChatWindow from "../components/ChatWindow"
import { useChat } from "../hooks/useChat"
import { useAppStore } from "../store"


function ChatPage() {
    const { sendMessage, pause, loading } = useChat()
    const currentProjectId = useAppStore((state) => state.currentProjectId)
    const currentSessionId = useAppStore((state) => state.currentSessionId)
    const drafts = useAppStore((state) => state.drafts)
    const setDraft = useAppStore((state) => state.setDraft)
    const draftKey = `${currentProjectId ?? "none"}:${currentSessionId ?? "new"}`
    const [question, setQuestion] = useState(drafts[draftKey] || "")
    const textareaRef = useRef<HTMLTextAreaElement>(null)

    useEffect(() => {
        setQuestion(drafts[draftKey] || "")
    }, [draftKey])

    useEffect(() => {
        const el = textareaRef.current
        if (!el) {
            return
        }
        const maxHeight = window.innerHeight * 0.5
        el.style.height = "auto"
        el.style.height = `${Math.min(el.scrollHeight, maxHeight)}px`
        el.style.overflowY = el.scrollHeight > maxHeight ? "auto" : "hidden"
    }, [question])

    const handleSend = async () => {
        const text = question.trim()
        if (!text || loading) {
            return
        }
        setQuestion("")
        setDraft(draftKey, "")
        await sendMessage(text)
    }

    return (
        <div className="chat-page">
            <div className="chat-window-wrap">
                <ChatWindow />
            </div>
            <div className="chat-input-row">
                <textarea
                    ref={textareaRef}
                    value={question}
                    onChange={(event) => {
                        setQuestion(event.target.value)
                        setDraft(draftKey, event.target.value)
                    }}
                    onKeyDown={(event) => {
                        if (event.key === "Enter" && !event.shiftKey) {
                            event.preventDefault()
                            handleSend()
                        }
                    }}
                    placeholder="输入您的问题，Enter 发送，Shift + Enter 换行..."
                    rows={4}
                />
                <button
                    type="button"
                    onClick={loading ? pause : handleSend}
                >
                    {loading ? "暂停" : "发送"}
                </button>
            </div>
        </div>
    )
}


export default ChatPage
