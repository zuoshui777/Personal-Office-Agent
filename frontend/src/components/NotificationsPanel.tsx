import { useEffect } from "react"

import {
    getNotifications,
    markAllNotificationsRead,
    streamNotifications
} from "../services/api"
import { useAppStore } from "../store"


interface Props {
    open: boolean
    onClose: () => void
}


export default function NotificationsPanel({ open, onClose }: Props) {
    const notifications = useAppStore((state) => state.notifications)
    const setNotifications = useAppStore((state) => state.setNotifications)
    const addNotifications = useAppStore((state) => state.addNotifications)

    useEffect(() => {
        getNotifications()
            .then(setNotifications)
            .catch(() => undefined)

        return streamNotifications(addNotifications)
    }, [addNotifications, setNotifications])

    if (!open) {
        return null
    }

    const unreadCount = notifications.filter((item) => !item.is_read).length

    return (
        <div
            className="notification-panel"
            onMouseLeave={onClose}
        >
            <div className="notification-panel-head">
                <strong>通知</strong>
                {unreadCount > 0 && (
                    <button
                        type="button"
                        onClick={() => {
                            markAllNotificationsRead()
                                .then(() => {
                                    setNotifications(
                                        notifications.map((item) => ({
                                            ...item,
                                            is_read: true
                                        }))
                                    )
                                })
                                .catch(() => undefined)
                        }}
                    >
                        全部已读
                    </button>
                )}
            </div>
            <div className="notification-list">
                {notifications.length === 0 && (
                    <div className="empty-state">暂无通知</div>
                )}
                {notifications.map((item) => (
                    <div
                        key={item.id}
                        className={`notification-item ${item.is_read ? "" : "unread"}`}
                    >
                        <div className="notification-title">{item.title}</div>
                        {item.content && (
                            <div className="notification-content">{item.content}</div>
                        )}
                    </div>
                ))}
            </div>
        </div>
    )
}
