import { useEffect, useMemo, useRef, useState } from "react"
import type { ChangeEvent } from "react"
import { FolderSync, RefreshCw } from "lucide-react"

import {
    deleteDocument,
    getDocumentStats,
    getDocumentsFiltered,
    syncFolder,
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


export default function KnowledgePage() {
    const currentProjectId = useAppStore((state) => state.currentProjectId)
    const knowledgeVersion = useAppStore((state) => state.knowledgeVersion)
    const bumpKnowledgeVersion = useAppStore((state) => state.bumpKnowledgeVersion)
    const [files, setFiles] = useState<any[]>([])
    const [stats, setStats] = useState<any>(null)
    const [search, setSearch] = useState("")
    const [category, setCategory] = useState("")
    const [sort, setSort] = useState("created_at")
    const [order, setOrder] = useState("desc")
    const [syncPath, setSyncPath] = useState("")
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

    const handleSync = async () => {
        if (!syncPath.trim() || !currentProjectId) {
            setMessage("请输入文件夹路径")
            return
        }
        setMessage("正在同步文件夹...")
        try {
            const result = await syncFolder(syncPath.trim(), currentProjectId)
            setMessage(`同步完成：发现 ${result.found} 个，索引 ${result.indexed} 个`)
            bumpKnowledgeVersion()
        } catch (error: any) {
            setMessage(error.message || "同步失败")
        }
    }

    return (
        <div className="page-panel">
            <div className="page-panel-head">
                <div>
                    <h2>知识库</h2>
                    <p>管理当前项目的文件与索引</p>
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
                        className="primary-button"
                        onClick={() => fileInputRef.current?.click()}
                    >
                        上传文件
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
                    className="text-input search-input"
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

            <div className="sync-row">
                <input
                    className="text-input"
                    value={syncPath}
                    onChange={(event) => setSyncPath(event.target.value)}
                    placeholder="/home/user/Documents/AI-Knowledge"
                />
                <button type="button" className="primary-button" onClick={handleSync}>
                    <FolderSync size={16} />
                    文件夹同步
                </button>
            </div>

            {message && <div className="form-message">{message}</div>}

            <div className="file-table">
                <div className="file-row file-row-head">
                    <span>文件名</span>
                    <span>分类</span>
                    <span>大小</span>
                    <span>操作</span>
                </div>
                {filteredFiles.length === 0 && (
                    <div className="empty-state">暂无文件</div>
                )}
                {filteredFiles.map((file) => (
                    <div className="file-row" key={file.id}>
                        <span>{file.file_name}</span>
                        <span>{file.category}</span>
                        <span>{formatSize(file.file_size)}</span>
                        <span>
                            <button
                                type="button"
                                className="danger-button"
                                onClick={() => handleDelete(file.id, file.file_name)}
                            >
                                删除
                            </button>
                        </span>
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
        </div>
    )
}
