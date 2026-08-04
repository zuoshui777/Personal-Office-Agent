// 聊天窗口
// 显示历史消息
// 增加自动滚动和AI思考状态


import MessageItem from "./MessageItem"

import { useChat } from "../hooks/useChat"
import { useAppStore } from "../store"

import {
    useEffect,
    useRef,
    useState
} from "react"
import type { UIEvent } from "react"



function ChatWindow(){


    const {

        messages,

        loading

    } = useChat()



    const bottomRef =
        useRef<HTMLDivElement>(null)
    const [stickToBottom, setStickToBottom] = useState(true)
    const scrollToken = useAppStore((state) => state.scrollToken)
    const scrollPaused = useAppStore((state) => state.scrollPaused)
    const setScrollPaused = useAppStore((state) => state.setScrollPaused)
    const lastScrollTokenRef = useRef(0)



    // 新消息自动滚动到底部；用户上滑后停止强制滚动

    useEffect(()=>{

        if (scrollPaused) {
            return
        }

        const last = messages[messages.length - 1]
        if (last?.role === "user") {
            setStickToBottom(true)
            bottomRef.current?.scrollIntoView({ behavior: "auto" })
            return
        }

        if (scrollToken !== lastScrollTokenRef.current) {
            lastScrollTokenRef.current = scrollToken
            setStickToBottom(true)
            bottomRef.current?.scrollIntoView({ behavior: "auto" })
        }

        if (stickToBottom) {
            bottomRef.current?.scrollIntoView({

                behavior:"smooth"

            })
        }


    },[messages,loading,stickToBottom,scrollToken,scrollPaused])

    const handleScroll = (event: UIEvent<HTMLDivElement>) => {
        const target = event.currentTarget
        const distance = target.scrollHeight - target.scrollTop - target.clientHeight
        setStickToBottom(distance < 80)
        setScrollPaused(distance >= 80)
    }




    return (

        <div

            style={{

                height:"65vh",

                overflowY:"auto",

                padding:"20px",

                background:"var(--surface)",

                borderRadius:"12px",

                border:"1px solid var(--border)"

            }}
            onScroll={handleScroll}

        >



            {


                messages.map(

                    (msg,index)=>(

                        <MessageItem

                            key={index}

                            role={msg.role}

                            content={msg.content}

                            sources={msg.sources}

                        />

                    )

                )


            }


            <div ref={bottomRef}/>



        </div>

    )

}


export default ChatWindow
