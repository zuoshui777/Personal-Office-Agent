import type {
    ChatSession,
    Message,
    NotificationItem,
    Project,
    User
} from "../store"


const BASE_URL = "http://localhost:8000"


function getToken() {
    return localStorage.getItem("token")
}


async function request<T>(
    path: string,
    options: RequestInit = {}
): Promise<T> {
    const token = getToken()
    const headers = new Headers(options.headers || {})
    if (token) {
        headers.set("Authorization", `Bearer ${token}`)
    }

    const body = options.body
    if (body && !(body instanceof FormData)) {
        headers.set("Content-Type", "application/json")
    }

    const res = await fetch(`${BASE_URL}${path}`, {
        ...options,
        headers
    })

    if (!res.ok) {
        let detail = res.statusText
        try {
            const data = await res.json()
            detail = data.detail || JSON.stringify(data)
        } catch {
            // keep status text
        }
        throw new Error(detail)
    }

    return res.json()
}


export async function login(username: string, password: string): Promise<any> {
    const body = new URLSearchParams()
    body.append("username", username)
    body.append("password", password)

    const res = await fetch(`${BASE_URL}/auth/login`, {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded"
        },
        body
    })
    const data = await res.json()
    if (data.access_token) {
        localStorage.setItem("token", data.access_token)
    }
    return data
}


export function register(username: string, password: string): Promise<any> {
    return request("/auth/register", {
        method: "POST",
        body: JSON.stringify({ username, password })
    })
}


export function getCurrentUser(): Promise<User> {
    return request<User>("/auth/me")
}


export function getProjects(): Promise<Project[]> {
    return request<Project[]>("/projects/")
}


export function createProject(projectName: string, description = ""): Promise<any> {
    return request<any>("/projects/", {
        method: "POST",
        body: JSON.stringify({
            project_name: projectName,
            description
        })
    })
}


export function deleteProject(projectId: number): Promise<any> {
    return request<any>(`/projects/${projectId}`, {
        method: "DELETE"
    })
}


export function getDocuments(projectId: number): Promise<any[]> {
    return request<any[]>(`/documents/?project_id=${projectId}`)
}


export function getDocumentsFiltered(
    projectId: number,
    category?: string,
    sort?: string,
    order?: string
): Promise<any[]> {
    const params = new URLSearchParams({ project_id: String(projectId) })
    if (category) {
        params.set("category", category)
    }
    if (sort) {
        params.set("sort", sort)
    }
    if (order) {
        params.set("order", order)
    }
    return request<any[]>(`/documents/?${params.toString()}`)
}


export function getDocumentStats(projectId: number): Promise<any> {
    return request<any>(`/documents/stats?project_id=${projectId}`)
}


export function deleteDocument(documentId: number): Promise<any> {
    return request<any>(`/documents/${documentId}`, {
        method: "DELETE"
    })
}


export function uploadDocument(projectId: number, file: File): Promise<any> {
    const formData = new FormData()
    formData.append("file", file)
    return request<any>(`/upload/?project_id=${projectId}`, {
        method: "POST",
        body: formData
    })
}


export function chat(
    question: string,
    session_id?: string,
    project_id?: number | null
): Promise<any> {
    return request<any>("/chat/", {
        method: "POST",
        body: JSON.stringify({
            question,
            session_id,
            project_id
        })
    })
}


export function getChatHistory(projectId?: number | null): Promise<ChatSession[]> {
    const query = projectId ? `?project_id=${projectId}` : ""
    return request<ChatSession[]>(`/chat/history/${query}`)
}


export function getChatMessages(sessionId: string): Promise<Message[]> {
    return request<Message[]>(`/chat/history/${sessionId}`)
}


export function deleteChatHistory(sessionId: string): Promise<any> {
    return request<any>(`/chat/history/${sessionId}`, {
        method: "DELETE"
    })
}


export function searchRag(query: string, projectId?: number | null): Promise<any> {
    return request<any>("/search/", {
        method: "POST",
        body: JSON.stringify({
            query,
            project_id: projectId
        })
    })
}


export function searchGlobal(query: string, projectId?: number | null): Promise<any> {
    const queryString = new URLSearchParams({ q: query })
    if (projectId) {
        queryString.set("project_id", String(projectId))
    }
    return request<any>(`/search/global?${queryString.toString()}`)
}


export function getNotifications(): Promise<NotificationItem[]> {
    return request<NotificationItem[]>("/notifications/")
}


export function markAllNotificationsRead(): Promise<any> {
    return request<any>("/notifications/read-all", {
        method: "POST"
    })
}


export function getSettings(): Promise<any> {
    return request<any>("/settings/")
}


export function updateSettings(payload: {
    llm_base_url: string
    llm_api_key: string
    llm_model: string
}) {
    return request<any>("/settings/", {
        method: "PUT",
        body: JSON.stringify(payload)
    })
}


export function getWeChatWebhook(): Promise<any> {
    return request<any>("/settings/wechat")
}


export function saveWeChatWebhook(webhookUrl: string): Promise<any> {
    return request<any>("/settings/wechat", {
        method: "PUT",
        body: JSON.stringify({ webhook_url: webhookUrl })
    })
}


export function deleteWeChatWebhook(): Promise<any> {
    return request<any>("/settings/wechat", {
        method: "DELETE"
    })
}


export function testWeChatWebhook(webhookUrl?: string): Promise<any> {
    return request<any>("/settings/wechat/test", {
        method: "POST",
        body: JSON.stringify({ webhook_url: webhookUrl || "" })
    })
}


export function runMimoTool(imagePath: string, prompt?: string): Promise<any> {
    return request<any>("/tools/mimo", {
        method: "POST",
        body: JSON.stringify({
            image_path: imagePath,
            prompt
        })
    })
}


export function runRagTool(query: string, projectId?: number | null): Promise<any> {
    return request<any>("/tools/rag", {
        method: "POST",
        body: JSON.stringify({
            query,
            project_id: projectId
        })
    })
}


export function getMCPTools(): Promise<any> {
    return request<any>("/tools/mcp")
}


export function toggleMCPTool(name: string, enabled: boolean): Promise<any> {
    return request<any>(`/tools/mcp/${name}/toggle`, {
        method: "POST",
        body: JSON.stringify({ enabled })
    })
}


export function executeMCPTool(name: string, arguments_: Record<string, any>): Promise<any> {
    return request<any>("/tools/mcp/execute", {
        method: "POST",
        body: JSON.stringify({ name, arguments: arguments_ })
    })
}


export function getAgents(): Promise<any> {
    return request<any>("/tools/agents")
}


export function toggleAgent(name: string, enabled: boolean): Promise<any> {
    return request<any>(`/tools/agents/${name}/toggle`, {
        method: "POST",
        body: JSON.stringify({ enabled })
    })
}


export function getSkills(): Promise<any> {
    return request<any>("/tools/skills")
}


export function getMemories(): Promise<any[]> {
    return request<any[]>("/memories/")
}


export function createMemory(key: string, value: string): Promise<any> {
    return request<any>("/memories/", {
        method: "POST",
        body: JSON.stringify({ key, value })
    })
}


export function deleteMemory(memoryId: number): Promise<any> {
    return request<any>(`/memories/${memoryId}`, {
        method: "DELETE"
    })
}


export function getTasks(): Promise<any[]> {
    return request<any[]>("/tasks/")
}


export function createTask(taskName: string, prompt: string, projectId?: number | null): Promise<any> {
    return request<any>("/tasks/", {
        method: "POST",
        body: JSON.stringify({
            task_name: taskName,
            prompt,
            project_id: projectId
        })
    })
}


export function getTask(taskId: number): Promise<any> {
    return request<any>(`/tasks/${taskId}`)
}


export function syncFolder(folderPath: string, projectId: number): Promise<any> {
    return request<any>("/sync/folder", {
        method: "POST",
        body: JSON.stringify({
            folder_path: folderPath,
            project_id: projectId
        })
    })
}


export async function streamChat(
    question: string,
    session_id: string | undefined,
    project_id: number | null | undefined,
    onMessage: (text: string) => void,
    onFinish: (data: any) => void,
    signal?: AbortSignal
) {
    const response = await fetch(`${BASE_URL}/chat/stream`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${getToken()}`
        },
        body: JSON.stringify({
            question,
            session_id,
            project_id
        }),
        signal
    })

    const reader = response.body?.getReader()
    const decoder = new TextDecoder()
    if (!reader) {
        return
    }

    let buffer = ""
    while (true) {
        const { done, value } = await reader.read()
        if (done) {
            break
        }
        if (signal?.aborted) {
            break
        }
        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split("\n")
        buffer = lines.pop() || ""

        for (const line of lines) {
            if (!line.startsWith("data:")) {
                continue
            }
            const data = line.replace("data:", "").trim()
            if (!data) {
                continue
            }
            const json = JSON.parse(data)
            if (json.content) {
                onMessage(json.content)
            }
            if (json.done) {
                onFinish(json)
            }
        }
    }
}


export function streamNotifications(
    onItems: (items: NotificationItem[]) => void
) {
    const controller = new AbortController()

    const run = async () => {
        const response = await fetch(`${BASE_URL}/notifications/stream`, {
            headers: {
                Authorization: `Bearer ${getToken()}`
            },
            signal: controller.signal
        })
        const reader = response.body?.getReader()
        const decoder = new TextDecoder()
        if (!reader) {
            return
        }

        let buffer = ""
        while (true) {
            const { done, value } = await reader.read()
            if (done) {
                break
            }
            buffer += decoder.decode(value, { stream: true })
            const lines = buffer.split("\n")
            buffer = lines.pop() || ""

            for (const line of lines) {
                if (!line.startsWith("data:")) {
                    continue
                }
                const data = line.replace("data:", "").trim()
                if (!data) {
                    continue
                }
                try {
                    const json = JSON.parse(data)
                    if (json.items) {
                        onItems(json.items)
                    }
                } catch {
                    // ignore partial events
                }
            }
        }
    }

    run().catch(() => undefined)
    return () => controller.abort()
}
