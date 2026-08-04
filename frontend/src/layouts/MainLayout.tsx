import { useState } from "react"
import {
    Bell,
    Moon,
    Search,
    Sun
} from "lucide-react"

import Sidebar from "../components/Sidebar"
import KnowledgePanel from "../components/KnowledgePanel"
import SearchOverlay from "../components/SearchOverlay"
import NotificationsPanel from "../components/NotificationsPanel"
import ChatPage from "../pages/ChatPage"
import KnowledgePage from "../pages/KnowledgePage"
import ProjectPage from "../pages/ProjectPage"
import PluginsPage from "../pages/PluginsPage"
import SettingsPage from "../pages/SettingsPage"
import { useAppStore } from "../store"


const NAV_TITLES: Record<string, string> = {
    chat: "聊天助手",
    knowledge: "知识库",
    projects: "项目中心",
    plugins: "工具中心",
    settings: "设置"
}


function MainLayout() {
    const activeNav = useAppStore((state) => state.activeNav)
    const searchOpen = useAppStore((state) => state.searchOpen)
    const setSearchOpen = useAppStore((state) => state.setSearchOpen)
    const theme = useAppStore((state) => state.theme)
    const toggleTheme = useAppStore((state) => state.toggleTheme)
    const notifications = useAppStore((state) => state.notifications)
    const [notificationsOpen, setNotificationsOpen] = useState(false)

    const unreadCount = notifications.filter((item) => !item.is_read).length

    return (
        <div className="app-shell">
            <Sidebar />

            <main className="main-area">
                <div className="topbar">
                    <div>
                        <h1>{NAV_TITLES[activeNav] || "聊天助手"}</h1>
                        <p>您的个人 AI 办公助手</p>
                    </div>
                    <div className="topbar-actions">
                        <button
                            type="button"
                            title="全局搜索"
                            onClick={() => setSearchOpen(true)}
                        >
                            <Search size={18} />
                        </button>
                        <button
                            type="button"
                            title="通知"
                            onClick={() => setNotificationsOpen((value) => !value)}
                        >
                            <Bell size={18} />
                            {unreadCount > 0 && (
                                <span className="badge">{unreadCount}</span>
                            )}
                        </button>
                        <button
                            type="button"
                            title={theme === "light" ? "夜间模式" : "日间模式"}
                            onClick={toggleTheme}
                        >
                            {theme === "light" ? <Moon size={18} /> : <Sun size={18} />}
                        </button>
                    </div>
                </div>

                <div className="main-content">
                    {activeNav === "chat" && <ChatPage />}
                    {activeNav === "knowledge" && <KnowledgePage />}
                    {activeNav === "projects" && <ProjectPage />}
                    {activeNav === "plugins" && <PluginsPage />}
                    {activeNav === "settings" && <SettingsPage />}
                </div>
            </main>

            <KnowledgePanel />

            <SearchOverlay
                open={searchOpen}
                onClose={() => setSearchOpen(false)}
            />
            <NotificationsPanel
                open={notificationsOpen}
                onClose={() => setNotificationsOpen(false)}
            />
        </div>
    )
}


export default MainLayout
