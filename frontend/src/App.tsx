import { useEffect } from "react"

import MainLayout from "./layouts/MainLayout"
import Login from "./pages/Login"
import { getCurrentUser, getProjects } from "./services/api"
import { useAppStore } from "./store"


function App() {
    const token = localStorage.getItem("token")
    const user = useAppStore((state) => state.user)
    const projects = useAppStore((state) => state.projects)
    const currentProjectId = useAppStore((state) => state.currentProjectId)
    const setUser = useAppStore((state) => state.setUser)
    const setProjects = useAppStore((state) => state.setProjects)
    const setCurrentProjectId = useAppStore((state) => state.setCurrentProjectId)

    useEffect(() => {
        const theme = localStorage.getItem("theme") || "light"
        document.documentElement.setAttribute("data-theme", theme)

        if (!token) {
            return
        }

        Promise.all([getCurrentUser(), getProjects()])
            .then(([userData, projectData]) => {
                setUser(userData)
                setProjects(projectData)

                const storedProjectId = Number(localStorage.getItem("currentProjectId"))
                const exists = projectData.some(
                    (project: any) => project.id === storedProjectId
                )
                const nextProjectId = exists
                    ? storedProjectId
                    : projectData[0]?.id || null

                setCurrentProjectId(nextProjectId)
                if (nextProjectId) {
                    localStorage.setItem("currentProjectId", String(nextProjectId))
                }
            })
            .catch(() => {
                localStorage.removeItem("token")
                setUser(null)
            })
    }, [token, setCurrentProjectId, setProjects, setUser])

    if (!token || (!user && !projects.length && currentProjectId === null)) {
        return <Login />
    }

    return <MainLayout />
}


export default App
