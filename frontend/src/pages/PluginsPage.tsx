import { useEffect, useState } from "react"

import {
    getAgents,
    getMCPTools,
    getSkills,
    runMimoTool,
    runRagTool,
    toggleAgent as toggleAgentApi,
    toggleMCPTool
} from "../services/api"
import { useAppStore } from "../store"


type Tab = "rag" | "mimo" | "mcp" | "skills" | "agents"


export default function PluginsPage() {
    const currentProjectId = useAppStore((state) => state.currentProjectId)
    const [tab, setTab] = useState<Tab>("mcp")
    const [ragQuery, setRagQuery] = useState("")
    const [ragResult, setRagResult] = useState<any[]>([])
    const [imagePath, setImagePath] = useState("")
    const [imagePrompt, setImagePrompt] = useState("")
    const [mimoResult, setMimoResult] = useState("")
    const [mcpTools, setMcpTools] = useState<any[]>([])
    const [skills, setSkills] = useState<any[]>([])
    const [agents, setAgents] = useState<any[]>([])
    const [message, setMessage] = useState("")

    const refreshManagement = async () => {
        const [toolData, skillData, agentData] = await Promise.all([
            getMCPTools(),
            getSkills(),
            getAgents()
        ])
        setMcpTools(toolData.tools || [])
        setSkills(skillData.skills || [])
        setAgents(agentData.agents || [])
    }

    useEffect(() => {
        refreshManagement().catch(() => undefined)
    }, [])

    const handleRag = async () => {
        if (!ragQuery.trim()) {
            return
        }
        try {
            const data = await runRagTool(ragQuery, currentProjectId)
            setRagResult(data.results || [])
            setMessage("知识库检索完成")
        } catch (error: any) {
            setMessage(error.message || "检索失败")
        }
    }

    const handleMimo = async () => {
        if (!imagePath.trim()) {
            setMessage("请输入本地图片路径")
            return
        }
        try {
            const data = await runMimoTool(
                imagePath.trim(),
                imagePrompt.trim() || undefined
            )
            setMimoResult(data.content || "")
            setMessage("MIMO 识别完成")
        } catch (error: any) {
            setMessage(error.message || "MIMO 识别失败")
        }
    }

    const toggleMcp = async (name: string, enabled: boolean) => {
        await toggleMCPTool(name, enabled)
        await refreshManagement()
    }

    const toggleAgent = async (name: string, enabled: boolean) => {
        await toggleAgentApi(name, enabled)
        await refreshManagement()
    }

    return (
        <div className="page-panel">
            <div className="page-panel-head">
                <div>
                    <h2>工具中心</h2>
                    <p>MCP、Skill、Agent 管理与真实工具执行</p>
                </div>
            </div>

            <div className="management-tabs">
                {([
                    ["mcp", "MCP 工具"],
                    ["skills", "Skills"],
                    ["agents", "Agent 管理"],
                    ["rag", "知识库检索"],
                    ["mimo", "MIMO 图片识别"]
                ] as [Tab, string][]).map(([id, label]) => (
                    <button
                        key={id}
                        type="button"
                        className={tab === id ? "active" : ""}
                        onClick={() => setTab(id)}
                    >
                        {label}
                    </button>
                ))}
            </div>

            {message && <div className="form-message">{message}</div>}

            {tab === "mcp" && (
                <div className="management-panel">
                    <div className="tool-list">
                        {mcpTools.map((tool) => (
                            <div className="management-item" key={tool.name}>
                                <div>
                                    <strong>{tool.name}</strong>
                                    <p>{tool.description}</p>
                                    <small>权限：{tool.permission}</small>
                                    <small>参数：{(tool.parameters || []).join(", ") || "无"}</small>
                                </div>
                                <button
                                    type="button"
                                    onClick={() => toggleMcp(tool.name, !tool.enabled)}
                                >
                                    {tool.enabled ? "禁用" : "启用"}
                                </button>
                            </div>
                        ))}
                    </div>

                </div>
            )}

            {tab === "skills" && (
                <div className="management-panel">
                    <div className="tool-list">
                        {skills.map((skill) => (
                            <div className="management-item" key={skill.path}>
                                <div>
                                    <strong>{skill.name}</strong>
                                    <p>{skill.description || "暂无描述"}</p>
                                    <small>{skill.path}</small>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {tab === "agents" && (
                <div className="management-panel">
                    <div className="tool-list">
                        {agents.map((agent) => (
                            <div className="management-item" key={agent.name}>
                                <div>
                                    <strong>{agent.label}</strong>
                                    <p>{agent.description}</p>
                                </div>
                                <button
                                    type="button"
                                    onClick={() => toggleAgent(agent.name, !agent.enabled)}
                                >
                                    {agent.enabled ? "禁用" : "启用"}
                                </button>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {tab === "rag" && (
                <div className="tool-card">
                    <h3>知识库检索</h3>
                    <input
                        className="text-input"
                        value={ragQuery}
                        onChange={(event) => setRagQuery(event.target.value)}
                        placeholder="输入检索问题"
                    />
                    <button type="button" className="primary-button" onClick={handleRag}>
                        检索
                    </button>
                    <div className="tool-result">
                        {ragResult.map((item, index) => (
                            <div key={index}>
                                <strong>{item.file_name}</strong>
                                <p>{item.text}</p>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {tab === "mimo" && (
                <div className="tool-card">
                    <h3>MIMO 图片识别</h3>
                    <input
                        className="text-input"
                        value={imagePath}
                        onChange={(event) => setImagePath(event.target.value)}
                        placeholder="本地图片路径"
                    />
                    <input
                        className="text-input"
                        value={imagePrompt}
                        onChange={(event) => setImagePrompt(event.target.value)}
                        placeholder="识别要求，可留空"
                    />
                    <button type="button" className="primary-button" onClick={handleMimo}>
                        开始识别
                    </button>
                    {mimoResult && <pre className="tool-result">{mimoResult}</pre>}
                </div>
            )}
        </div>
    )
}
