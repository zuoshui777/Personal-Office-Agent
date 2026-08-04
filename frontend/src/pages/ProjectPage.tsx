import { useState } from "react"

import {
    createProject,
    deleteProject,
    getProjects
} from "../services/api"
import { useAppStore } from "../store"


export default function ProjectPage() {
    const projects = useAppStore((state) => state.projects)
    const setProjects = useAppStore((state) => state.setProjects)
    const currentProjectId = useAppStore((state) => state.currentProjectId)
    const setCurrentProjectId = useAppStore((state) => state.setCurrentProjectId)
    const setMessages = useAppStore((state) => state.setMessages)
    const setCurrentSession = useAppStore((state) => state.setCurrentSession)
    const bumpKnowledgeVersion = useAppStore((state) => state.bumpKnowledgeVersion)
    const [name, setName] = useState("")
    const [description, setDescription] = useState("")
    const [message, setMessage] = useState("")

    const refreshProjects = async () => {
        const data = await getProjects()
        setProjects(data)
    }

    const switchProject = (id: number | null) => {
        setCurrentProjectId(id)
        if (id) {
            localStorage.setItem("currentProjectId", String(id))
        } else {
            localStorage.removeItem("currentProjectId")
        }
        setMessages([])
        setCurrentSession(null)
        bumpKnowledgeVersion()
    }

    const handleCreate = async () => {
        if (!name.trim()) {
            setMessage("请输入项目名称")
            return
        }
        try {
            const result = await createProject(name.trim(), description.trim())
            setMessage(`项目创建成功：${result.project_name}`)
            setName("")
            setDescription("")
            await refreshProjects()
            bumpKnowledgeVersion()
            switchProject(result.project_id)
        } catch (error: any) {
            setMessage(error.message || "创建失败")
        }
    }

    const handleDelete = async (id: number, projectName: string) => {
        if (!window.confirm(`确认删除项目 ${projectName}？相关文件也会删除。`)) {
            return
        }
        try {
            await deleteProject(id)
            setMessage("项目删除成功")
            const data = await getProjects()
            setProjects(data)
            bumpKnowledgeVersion()
            if (currentProjectId === id) {
                const next = data[0]?.id || null
                switchProject(next)
            }
        } catch (error: any) {
            setMessage(error.message || "删除失败")
        }
    }

    return (
        <div className="page-panel">
            <div className="page-panel-head">
                <div>
                    <h2>项目中心</h2>
                    <p>创建、切换和管理独立知识库项目</p>
                </div>
            </div>

            <div className="form-grid">
                <input
                    className="text-input"
                    value={name}
                    onChange={(event) => setName(event.target.value)}
                    placeholder="项目名称"
                />
                <input
                    className="text-input"
                    value={description}
                    onChange={(event) => setDescription(event.target.value)}
                    placeholder="项目描述"
                />
                <button type="button" className="primary-button" onClick={handleCreate}>
                    创建项目
                </button>
            </div>

            {message && <div className="form-message">{message}</div>}

            <div className="project-grid">
                {projects.map((project) => (
                    <div
                        key={project.id}
                        className={`project-card ${
                            currentProjectId === project.id ? "active" : ""
                        }`}
                    >
                        <div>
                            <h3>{project.project_name}</h3>
                            <p>{project.description || "暂无描述"}</p>
                            <span>{project.document_count} 个文件</span>
                        </div>
                        <div className="project-card-actions">
                            <button
                                type="button"
                                className="primary-button"
                                onClick={() => switchProject(project.id)}
                            >
                                切换
                            </button>
                            <button
                                type="button"
                                className="danger-button"
                                onClick={() => handleDelete(project.id, project.project_name)}
                            >
                                删除
                            </button>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    )
}
