import { create } from "zustand"


export interface Message {
    role: "user" | "assistant"
    content: string
    sources?: string[]
}


export interface ChatSession {
    session_id: string
    title: string
    project_id?: number | null
    created_at: string
    updated_at: string
}


export interface User {
    id: number
    username: string
    role: string
}


export interface Project {
    id: number
    project_name: string
    description: string
    document_count: number
    created_at?: string
}


export interface NotificationItem {
    id: number
    title: string
    content: string
    type: string
    is_read: boolean
    created_at?: string
}


export type Theme = "light" | "dark"


interface AppState {
    user: User | null
    projects: Project[]
    currentProjectId: number | null
    theme: Theme
    notifications: NotificationItem[]
    searchOpen: boolean
    activeNav: string
    sidebarCollapsed: boolean
    knowledgeVersion: number
    scrollToken: number
    scrollPaused: boolean
    drafts: Record<string, string>

    sessions: ChatSession[]
    currentSessionId: string | null
    messages: Message[]
    loading: boolean

    setLoading: (loading: boolean) => void
    setSessions: (sessions: ChatSession[]) => void
    setCurrentSession: (sessionId: string | null) => void
    setMessages: (messages: Message[]) => void
    addMessage: (message: Message) => void
    updateLastMessage: (content: string) => void

    setUser: (user: User | null) => void
    setProjects: (projects: Project[]) => void
    setCurrentProjectId: (projectId: number | null) => void
    setTheme: (theme: Theme) => void
    toggleTheme: () => void
    setNotifications: (notifications: NotificationItem[]) => void
    addNotifications: (notifications: NotificationItem[]) => void
    setSearchOpen: (open: boolean) => void
    setActiveNav: (nav: string) => void
    setSidebarCollapsed: (collapsed: boolean) => void
    toggleSidebar: () => void
    bumpKnowledgeVersion: () => void
    bumpScrollToken: () => void
    setScrollPaused: (paused: boolean) => void
    setDraft: (key: string, value: string) => void
}


export const useAppStore = create<AppState>((set) => ({
    user: null,
    projects: [],
    currentProjectId: null,
    theme: (localStorage.getItem("theme") as Theme) || "light",
    notifications: [],
    searchOpen: false,
    activeNav: "chat",
    sidebarCollapsed: false,
    knowledgeVersion: 0,
    scrollToken: 0,
    scrollPaused: false,
    drafts: {},

    sessions: [],
    currentSessionId: null,
    messages: [],
    loading: false,

    setLoading: (loading) => set({ loading }),
    setSessions: (sessions) => set({ sessions }),
    setCurrentSession: (currentSessionId) => set({ currentSessionId }),
    setMessages: (messages) => set({ messages }),
    addMessage: (message) =>
        set((state) => ({
            messages: [...state.messages, message]
        })),
    updateLastMessage: (content) =>
        set((state) => {
            const messages = [...state.messages]
            if (messages.length) {
                messages[messages.length - 1].content = content
            }
            return { messages }
        }),

    setUser: (user) => set({ user }),
    setProjects: (projects) => set({ projects }),
    setCurrentProjectId: (currentProjectId) => set({ currentProjectId }),
    setTheme: (theme) => {
        localStorage.setItem("theme", theme)
        document.documentElement.setAttribute("data-theme", theme)
        set({ theme })
    },
    toggleTheme: () =>
        set((state) => {
            const theme = state.theme === "light" ? "dark" : "light"
            localStorage.setItem("theme", theme)
            document.documentElement.setAttribute("data-theme", theme)
            return { theme }
        }),
    setNotifications: (notifications) => set({ notifications }),
    addNotifications: (notifications) =>
        set((state) => ({
            notifications: [...notifications, ...state.notifications].slice(0, 100)
        })),
    setSearchOpen: (searchOpen) => set({ searchOpen }),
    setActiveNav: (activeNav) => set({ activeNav }),
    setSidebarCollapsed: (sidebarCollapsed) => set({ sidebarCollapsed }),
    toggleSidebar: () =>
        set((state) => ({
            sidebarCollapsed: !state.sidebarCollapsed
        })),
    bumpKnowledgeVersion: () =>
        set((state) => ({
            knowledgeVersion: state.knowledgeVersion + 1
        })),
    bumpScrollToken: () =>
        set((state) => ({
            scrollToken: state.scrollToken + 1
        })),
    setScrollPaused: (scrollPaused) => set({ scrollPaused }),
    setDraft: (key, value) =>
        set((state) => ({
            drafts: {
                ...state.drafts,
                [key]: value
            }
        }))
}))
