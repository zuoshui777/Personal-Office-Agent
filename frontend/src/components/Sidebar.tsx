import { useEffect } from "react"
import {
    FolderKanban,
    FolderOpen,
    MessageSquare,
    PanelLeftClose,
    PanelLeftOpen,
    Plus,
    Puzzle,
    Settings,
    Trash2
} from "lucide-react"

import {
    deleteChatHistory,
    getChatHistory,
    getChatMessages
} from "../services/api"
import { useAppStore } from "../store"


const NAV_ITEMS = [
    { id: "chat", label: "聊天助手", icon: MessageSquare },
    { id: "knowledge", label: "知识库", icon: FolderOpen },
    { id: "projects", label: "项目中心", icon: FolderKanban },
    { id: "plugins", label: "工具中心", icon: Puzzle },
    { id: "settings", label: "设置", icon: Settings }
]


function Sidebar() {
    const user = useAppStore((state) => state.user)
    const projects = useAppStore((state) => state.projects)
    const currentProjectId = useAppStore((state) => state.currentProjectId)
    const setCurrentProjectId = useAppStore((state) => state.setCurrentProjectId)
    const activeNav = useAppStore((state) => state.activeNav)
    const setActiveNav = useAppStore((state) => state.setActiveNav)
    const sessions = useAppStore((state) => state.sessions)
    const setSessions = useAppStore((state) => state.setSessions)
    const setMessages = useAppStore((state) => state.setMessages)
    const setCurrentSession = useAppStore((state) => state.setCurrentSession)
    const sidebarCollapsed = useAppStore((state) => state.sidebarCollapsed)
    const toggleSidebar = useAppStore((state) => state.toggleSidebar)

    useEffect(() => {
        getChatHistory(currentProjectId)
            .then(setSessions)
            .catch(() => setSessions([]))
    }, [currentProjectId, setSessions])

    const switchProject = (projectId: number) => {
        setCurrentProjectId(projectId)
        localStorage.setItem("currentProjectId", String(projectId))
        setMessages([])
        setCurrentSession(null)
    }

    const openSession = async (sessionId: string) => {
        setCurrentSession(sessionId)
        setActiveNav("chat")
        const data = await getChatMessages(sessionId)
        setMessages(data)
    }

    const newChat = () => {
        setMessages([])
        setCurrentSession(null)
        setActiveNav("chat")
    }

    return (
        <aside className={`sidebar ${sidebarCollapsed ? "collapsed" : ""}`}>
            <div className="sidebar-brand">
                <span className="brand-mark">U</span>
                <div>
                    <strong>Personal Office Agent</strong>
                    <small>AI 办公助手</small>
                </div>
            </div>

            <button
                type="button"
                className="sidebar-collapse-button"
                title={sidebarCollapsed ? "展开侧边栏" : "折叠侧边栏"}
                onClick={toggleSidebar}
            >
                {sidebarCollapsed ? <PanelLeftOpen size={18} /> : <PanelLeftClose size={18} />}
            </button>

            <select
                className="project-select"
                value={currentProjectId || ""}
                onChange={(event) => switchProject(Number(event.target.value))}
            >
                {projects.length === 0 && <option value="">暂无项目</option>}
                {projects.map((project) => (
                    <option key={project.id} value={project.id}>
                        {project.project_name}
                    </option>
                ))}
            </select>

            <nav className="sidebar-nav">
                {NAV_ITEMS.map((item) => {
                    const Icon = item.icon
                    return (
                        <button
                            key={item.id}
                            type="button"
                            className={activeNav === item.id ? "active" : ""}
                            onClick={() => setActiveNav(item.id)}
                        >
                            <Icon size={18} />
                            <span>{item.label}</span>
                        </button>
                    )
                })}
            </nav>

            <button type="button" className="new-chat-button" onClick={newChat}>
                <Plus size={16} />
                新建聊天
            </button>

            <div className="sidebar-section-title">
                <span>最近对话</span>
            </div>
            <div className="session-list">
                {sessions.length === 0 && (
                    <div className="sidebar-empty">暂无聊天记录</div>
                )}
                {sessions.map((item) => (
                    <div
                        key={item.session_id}
                        className="session-item"
                        onClick={() => openSession(item.session_id)}
                    >
                        <span>{item.title || "新聊天"}</span>
                        <button
                            type="button"
                            title="删除会话"
                            onClick={(event) => {
                                event.stopPropagation()
                                deleteChatHistory(item.session_id).then(() => {
                                    setSessions(sessions.filter((s) => s.session_id !== item.session_id))
                                }).catch(() => undefined)
                            }}
                        >
                            <Trash2 size={14} />
                        </button>
                    </div>
                ))}
            </div>

            <div className="sidebar-user">
                <div className="user-avatar">{user?.username?.slice(0, 1) || "U"}</div>
                <div>
                    <strong>{user?.username || "未登录"}</strong>
                    <small>{user?.role || "user"}</small>
                </div>
            </div>
        </aside>
    )
}


export default Sidebar
