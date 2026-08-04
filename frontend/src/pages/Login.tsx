import { useState } from "react"

import { login, register } from "../services/api"


function Login() {
    const [mode, setMode] = useState<"login" | "register">("login")
    const [username, setUsername] = useState("")
    const [password, setPassword] = useState("")
    const [message, setMessage] = useState("")

    const handleSubmit = async () => {
        if (!username || !password) {
            setMessage("请输入用户名和密码")
            return
        }

        try {
            if (mode === "register") {
                await register(username, password)
                setMessage("注册成功，请登录")
                setMode("login")
                return
            }

            const result = await login(username, password)
            if (result.access_token) {
                window.location.href = "/"
            } else {
                setMessage("登录失败")
            }
        } catch (error: any) {
            setMessage(error.message || "操作失败")
        }
    }

    return (
        <div
            style={{
                height: "100vh",
                display: "flex",
                justifyContent: "center",
                alignItems: "center",
                background: "var(--bg-app)",
                color: "var(--text-primary)"
            }}
        >
            <div
                style={{
                    width: "360px",
                    background: "var(--surface)",
                    border: "1px solid var(--border)",
                    padding: "30px",
                    borderRadius: "12px",
                    boxShadow: "0 4px 20px rgba(0,0,0,0.1)"
                }}
            >
                <h2 style={{ marginTop: 0 }}>Personal AI</h2>
                <p>{mode === "login" ? "登录系统" : "注册账号"}</p>

                <input
                    style={{
                        width: "100%",
                        padding: "10px",
                        marginBottom: "15px",
                        borderRadius: "8px",
                        border: "1px solid var(--border)",
                        background: "var(--surface-soft)",
                        color: "var(--text-primary)"
                    }}
                    placeholder="用户名"
                    value={username}
                    onChange={(event) => setUsername(event.target.value)}
                />

                <input
                    type="password"
                    style={{
                        width: "100%",
                        padding: "10px",
                        marginBottom: "15px",
                        borderRadius: "8px",
                        border: "1px solid var(--border)",
                        background: "var(--surface-soft)",
                        color: "var(--text-primary)"
                    }}
                    placeholder="密码"
                    value={password}
                    onChange={(event) => setPassword(event.target.value)}
                    onKeyDown={(event) => {
                        if (event.key === "Enter") {
                            handleSubmit()
                        }
                    }}
                />

                <button
                    type="button"
                    style={{
                        width: "100%",
                        padding: "10px",
                        background: "#2563eb",
                        color: "#fff",
                        border: "none",
                        borderRadius: "8px"
                    }}
                    onClick={handleSubmit}
                >
                    {mode === "login" ? "登录" : "注册"}
                </button>

                <button
                    type="button"
                    style={{
                        width: "100%",
                        marginTop: "10px",
                        padding: "8px",
                        background: "transparent",
                        color: "var(--text-secondary)",
                        border: "none",
                        cursor: "pointer"
                    }}
                    onClick={() => {
                        setMode(mode === "login" ? "register" : "login")
                        setMessage("")
                    }}
                >
                    {mode === "login" ? "没有账号？注册" : "已有账号？登录"}
                </button>

                <p>{message}</p>
            </div>
        </div>
    )
}


export default Login
