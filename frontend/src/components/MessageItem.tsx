// 单条聊天消息组件
// 用户消息右侧蓝色气泡
// AI消息左侧灰色气泡
// AI回答显示RAG参考来源


import ReactMarkdown from "react-markdown"

import remarkGfm from "remark-gfm"


interface Props{

    role:string

    content:string

    sources?:string[]

}



function MessageItem(
    {
        role,
        content,
        sources
    }:Props
){


    const isUser = role === "user"



    return (

        <div

            style={{

                display:"flex",

                justifyContent:
                    isUser
                    ?
                    "flex-end"
                    :
                    "flex-start",

                marginBottom:"16px"

            }}

        >



            <div

                style={{

                    maxWidth:
                        isUser
                        ?
                        "fit-content"
                        :
                        "75%",

                    padding:"12px 16px",

                    borderRadius:"12px",

                    background:
                        isUser
                        ?
                        "#2563eb"
                        :
                        "var(--bubble-ai)",

                    color:
                        isUser
                        ?
                        "white"
                        :
                        "var(--text-primary)",

                    lineHeight:"1.6",

                    animation:"fadeIn 0.25s ease"

                }}

            >



                {!isUser && (
                    <div
                        style={{
                            fontSize: "13px",
                            marginBottom: "5px",
                            opacity: 0.7
                        }}
                    >
                        AI
                    </div>
                )}




                <div

                    style={{
                        lineHeight:"1.7"
                }}
                >
                    <ReactMarkdown
                        remarkPlugins={[
                            remarkGfm
                        ]}
                    >
                        {content}

                    </ReactMarkdown>
                </div>




                {

                    !isUser

                    &&

                    sources

                    &&

                    sources.length>0

                    &&

                    (

                    <div

                        style={{

                            marginTop:"12px",

                            paddingTop:"10px",

                            borderTop:
                            "1px solid var(--border)",

                            fontSize:"13px",

                            color:"var(--text-secondary)"

                        }}

                    >

                        <div>
                            📚 参考来源：
                        </div>


                        {
                            sources.map(

                                (item,index)=>(

                                    <div key={index}>

                                        📄 {item}

                                    </div>

                                )

                            )
                        }


                    </div>

                    )

                }



            </div>


        </div>

    )

}


export default MessageItem
