import { useEffect, useState } from "react"

import {
    getChatMessages,
    searchGlobal
} from "../services/api"
import { useAppStore } from "../store"


interface Props {
    open: boolean
    onClose: () => void
}


export default function SearchOverlay({ open, onClose }: Props) {
    const currentProjectId = useAppStore((state) => state.currentProjectId)
    const setCurrentProjectId = useAppStore((state) => state.setCurrentProjectId)
    const setActiveNav = useAppStore((state) => state.setActiveNav)
    const setCurrentSession = useAppStore((state) => state.setCurrentSession)
    const setMessages = useAppStore((state) => state.setMessages)
    const [query, setQuery] = useState("")
    const [results, setResults] = useState<any>({
        projects: [],
        documents: [],
        sessions: []
    })

    useEffect(() => {
        if (!open) {
            setQuery("")
            setResults({ projects: [], documents: [], sessions: [] })
            return
        }

        if (query.trim().length < 1) {
            setResults({ projects: [], documents: [], sessions: [] })
            return
        }

        const timer = window.setTimeout(() => {
            searchGlobal(query.trim(), currentProjectId)
                .then(setResults)
                .catch(() => undefined)
        }, 300)

        return () => window.clearTimeout(timer)
    }, [open, query, currentProjectId])

    useEffect(() => {
        const handleKey = (event: KeyboardEvent) => {
            if (event.key === "Escape") {
                onClose()
            }
        }
        window.addEventListener("keydown", handleKey)
        return () => window.removeEventListener("keydown", handleKey)
    }, [onClose])

    if (!open) {
        return null
    }

    const openSession = async (sessionId: string) => {
        setCurrentSession(sessionId)
        setActiveNav("chat")
        const data = await getChatMessages(sessionId)
        setMessages(data)
        onClose()
    }

    return (
        <div className="search-overlay">
            <div className="search-overlay-card">
                <input
                    autoFocus
                    value={query}
                    onChange={(event) => setQuery(event.target.value)}
                    placeholder="搜索项目、文件、聊天记录..."
                />
                <div className="search-results">
                    <section>
                        <h4>项目</h4>
                        {results.projects.length === 0 && <div className="empty-state">无匹配项目</div>}
                        {results.projects.map((item: any) => (
                            <button
                                key={item.id}
                                type="button"
                                onClick={() => {
                                    setCurrentProjectId(item.id)
                                    localStorage.setItem("currentProjectId", String(item.id))
                                    setActiveNav("projects")
                                    onClose()
                                }}
                            >
                                {item.name}
                            </button>
                        ))}
                    </section>
                    <section>
                        <h4>文件</h4>
                        {results.documents.length === 0 && <div className="empty-state">无匹配文件</div>}
                        {results.documents.map((item: any) => (
                            <button
                                key={item.id}
                                type="button"
                                onClick={() => {
                                    setActiveNav("knowledge")
                                    onClose()
                                }}
                            >
                                {item.file_name}
                            </button>
                        ))}
                    </section>
                    <section>
                        <h4>聊天记录</h4>
                        {results.sessions.length === 0 && <div className="empty-state">无匹配聊天</div>}
                        {results.sessions.map((item: any) => (
                            <button
                                key={item.session_id}
                                type="button"
                                onClick={() => openSession(item.session_id)}
                            >
                                {item.title}
                            </button>
                        ))}
                    </section>
                </div>
            </div>
            <button
                type="button"
                className="search-overlay-close"
                onClick={onClose}
                aria-label="关闭搜索"
            >
                关闭
            </button>
        </div>
    )
}
