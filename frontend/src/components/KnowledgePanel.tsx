import { useEffect, useMemo, useRef, useState } from "react"
import type { ChangeEvent } from "react"
import {
    FileCode2,
    FileSpreadsheet,
    FileText,
    Image as ImageIcon,
    RefreshCw,
    Trash2,
    Upload
} from "lucide-react"

import {
    deleteDocument,
    getDocumentStats,
    getDocumentsFiltered,
    uploadDocument
} from "../services/api"
import { useAppStore } from "../store"


function formatSize(bytes: number) {
    if (!bytes) {
        return "-"
    }
    if (bytes < 1024 * 1024) {
        return `${(bytes / 1024).toFixed(1)} KB`
    }
    return `${(bytes / 1024 / 1024).toFixed(1)} MB`
}


const CATEGORIES = [
    { id: "", label: "全部文件" },
    { id: "document", label: "文档" },
    { id: "sheet", label: "表格" },
    { id: "image", label: "图片" },
    { id: "code", label: "代码" }
]


function FileIcon({ category }: { category: string }) {
    if (category === "sheet") {
        return <FileSpreadsheet size={18} />
    }
    if (category === "image") {
        return <ImageIcon size={18} />
    }
    if (category === "code") {
        return <FileCode2 size={18} />
    }
    return <FileText size={18} />
}


function KnowledgePanel() {
    const currentProjectId = useAppStore((state) => state.currentProjectId)
    const knowledgeVersion = useAppStore((state) => state.knowledgeVersion)
    const bumpKnowledgeVersion = useAppStore((state) => state.bumpKnowledgeVersion)
    const [files, setFiles] = useState<any[]>([])
    const [stats, setStats] = useState<any>(null)
    const [search, setSearch] = useState("")
    const [category, setCategory] = useState("")
    const [sort, setSort] = useState("created_at")
    const [order, setOrder] = useState("desc")
    const [message, setMessage] = useState("")
    const fileInputRef = useRef<HTMLInputElement>(null)

    const loadFiles = async () => {
        if (!currentProjectId) {
            setFiles([])
            setStats(null)
            return
        }
        const [fileData, statsData] = await Promise.all([
            getDocumentsFiltered(currentProjectId, category, sort, order),
            getDocumentStats(currentProjectId)
        ])
        setFiles(fileData)
        setStats(statsData)
    }

    useEffect(() => {
        loadFiles().catch(() => {
            setFiles([])
            setStats(null)
        })
    }, [currentProjectId, knowledgeVersion, category, sort, order])

    const filteredFiles = useMemo(() => {
        const q = search.trim().toLowerCase()
        if (!q) {
            return files
        }
        return files.filter((file) =>
            file.file_name.toLowerCase().includes(q)
        )
    }, [files, search])

    const handleUpload = async (event: ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0]
        if (!file || !currentProjectId) {
            return
        }
        setMessage("正在上传...")
        try {
            const result = await uploadDocument(currentProjectId, file)
            setMessage(`已加入队列：${result.file_name}`)
            bumpKnowledgeVersion()
        } catch (error: any) {
            setMessage(error.message || "上传失败")
        } finally {
            if (fileInputRef.current) {
                fileInputRef.current.value = ""
            }
        }
    }

    const handleDelete = async (id: number, name: string) => {
        if (!window.confirm(`确认删除 ${name}？`)) {
            return
        }
        try {
            await deleteDocument(id)
            setMessage("删除成功")
            bumpKnowledgeVersion()
        } catch (error: any) {
            setMessage(error.message || "删除失败")
        }
    }

    return (
        <aside className="knowledge-panel">
            <div className="knowledge-panel-head">
                <div>
                    <h3>知识库</h3>
                    <p>当前项目文件</p>
                </div>
                <div className="knowledge-actions">
                    <button
                        type="button"
                        className="icon-button"
                        title="刷新"
                        onClick={() => bumpKnowledgeVersion()}
                    >
                        <RefreshCw size={16} />
                    </button>
                    <button
                        type="button"
                        className="icon-button"
                        title="上传文件"
                        onClick={() => fileInputRef.current?.click()}
                    >
                        <Upload size={16} />
                    </button>
                </div>
                <input
                    ref={fileInputRef}
                    type="file"
                    hidden
                    onChange={handleUpload}
                />
            </div>

            <div className="category-tabs">
                {CATEGORIES.map((item) => (
                    <button
                        key={item.id}
                        type="button"
                        className={category === item.id ? "active" : ""}
                        onClick={() => setCategory(item.id)}
                    >
                        {item.label}
                    </button>
                ))}
            </div>

            <div className="knowledge-filter-row">
                <input
                    className="text-input"
                    value={search}
                    onChange={(event) => setSearch(event.target.value)}
                    placeholder="搜索文件..."
                />
                <select
                    className="text-input"
                    value={sort}
                    onChange={(event) => setSort(event.target.value)}
                >
                    <option value="created_at">按时间</option>
                    <option value="file_name">按名称</option>
                    <option value="file_size">按大小</option>
                </select>
                <button
                    type="button"
                    onClick={() => setOrder(order === "desc" ? "asc" : "desc")}
                >
                    {order === "desc" ? "降序" : "升序"}
                </button>
            </div>

            {message && <div className="form-message">{message}</div>}

            <div className="knowledge-file-list">
                {filteredFiles.length === 0 && (
                    <div className="empty-state">暂无文件</div>
                )}
                {filteredFiles.map((file) => (
                    <div className="knowledge-file-item" key={file.id}>
                        <FileIcon category={file.category} />
                        <div>
                            <strong>{file.file_name}</strong>
                            <span>
                                {file.file_type || "-"} · {formatSize(file.file_size)}
                            </span>
                        </div>
                        <button
                            type="button"
                            title="删除"
                            onClick={() => handleDelete(file.id, file.file_name)}
                        >
                            <Trash2 size={15} />
                        </button>
                    </div>
                ))}
            </div>

            {stats && (
                <div className="storage-summary">
                    <span>存储空间使用情况</span>
                    <strong>{stats.used_display} / {stats.capacity_display}</strong>
                    <div className="storage-bar">
                        <span style={{ width: `${stats.percent}%` }} />
                    </div>
                </div>
            )}
        </aside>
    )
}


export default KnowledgePanel
