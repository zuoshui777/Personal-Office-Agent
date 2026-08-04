import { useRef } from "react"

import {
    getChatHistory,
    streamChat
} from "../services/api"
import { useAppStore } from "../store"


export function useChat() {
    const abortControllerRef = useRef<AbortController | null>(null)
    const messages = useAppStore((state) => state.messages)
    const loading = useAppStore((state) => state.loading)
    const addMessage = useAppStore((state) => state.addMessage)
    const updateLastMessage = useAppStore((state) => state.updateLastMessage)
    const setMessages = useAppStore((state) => state.setMessages)
    const currentSessionId = useAppStore((state) => state.currentSessionId)
    const setCurrentSession = useAppStore((state) => state.setCurrentSession)
    const currentProjectId = useAppStore((state) => state.currentProjectId)
    const setSessions = useAppStore((state) => state.setSessions)
    const setLoading = useAppStore((state) => state.setLoading)
    const bumpScrollToken = useAppStore((state) => state.bumpScrollToken)
    const setScrollPaused = useAppStore((state) => state.setScrollPaused)

    async function sendMessage(question: string) {
        abortControllerRef.current?.abort()
        abortControllerRef.current = new AbortController()

        addMessage({ role: "user", content: question })
        setScrollPaused(false)
        bumpScrollToken()
        setLoading(true)
        addMessage({ role: "assistant", content: "正在思考" })

        let aiText = ""

        try {
            await streamChat(
                question,
                currentSessionId || undefined,
                currentProjectId,
                (text) => {
                    aiText += text
                    const latest = useAppStore.getState().messages
                    const last = latest[latest.length - 1]
                    if (!last || last.role !== "assistant") {
                        addMessage({
                            role: "assistant",
                            content: text
                        })
                    } else {
                        updateLastMessage(aiText)
                    }
                },
                (data) => {
                    if (data.session_id) {
                        setCurrentSession(data.session_id)
                    }

                    const latest = useAppStore.getState().messages
                    const next = [...latest]
                    const last = next[next.length - 1]
                    if (last) {
                        last.content = aiText || last.content
                        last.sources = data.sources || []
                        setMessages(next)
                    }

                    getChatHistory(currentProjectId)
                        .then(setSessions)
                        .catch(() => undefined)
                },
                abortControllerRef.current.signal
            )
        } catch (error: any) {
            if (error.name !== "AbortError") {
                const latest = useAppStore.getState().messages
                const last = latest[latest.length - 1]
                if (last && last.role === "assistant") {
                    updateLastMessage(error.message || "请求失败")
                } else {
                    addMessage({
                        role: "assistant",
                        content: error.message || "请求失败"
                    })
                }
            }
        } finally {
            setLoading(false)
            abortControllerRef.current = null
        }
    }

    const pause = () => {
        abortControllerRef.current?.abort()
        setScrollPaused(true)
        const current = useAppStore.getState().messages
        const next = current.filter((message) => !(
            message.role === "assistant" &&
            (
                message.content === "DeepSeek 正在思考" ||
                message.content === "正在思考" ||
                message.content === ""
            )
        ))
        setMessages(next)
        setLoading(false)
    }

    return {
        messages,
        sendMessage,
        pause,
        loading
    }
}
