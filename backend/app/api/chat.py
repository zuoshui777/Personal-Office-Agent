# 智能问答接口
# 提供聊天接口
# 支持普通返回 + SSE流式输出


from uuid import uuid4

import json
import asyncio


from fastapi import (
    APIRouter,
    Depends
)

from fastapi.responses import StreamingResponse


from sqlalchemy.orm import Session


from app.services.chat_service import answer_question


from app.database.connection import get_db

from app.core.dependencies import get_current_user, resolve_project_id

from app.models.user import User

from app.schemas.chat import ChatRequest



router = APIRouter(

    prefix="/chat",

    tags=["智能问答"]

)





# =========================
# 普通聊天接口
# =========================

@router.post("/")
def chat(

    request:ChatRequest,

    db:Session = Depends(get_db),

    current_user:User = Depends(get_current_user)

):


    session_id = request.session_id


    if session_id is None:

        session_id = str(uuid4())

    project_id = resolve_project_id(
        db,
        current_user,
        request.project_id
    )


    result = answer_question(

        request.question,

        current_user.id,

        db,

        session_id,
        project_id

    )


    return {


        "question":
            request.question,


        "answer":
            result["answer"],


        "sources":
            result["sources"],


        "session_id":
            result["session_id"]

    }





# =========================
# SSE流式聊天接口
# =========================

@router.post("/stream")
def chat_stream(

    request:ChatRequest,

    db:Session = Depends(get_db),

    current_user:User = Depends(get_current_user)

):



    session_id = request.session_id



    if session_id is None:

        session_id = str(uuid4())

    project_id = resolve_project_id(
        db,
        current_user,
        request.project_id
    )




    async def event_generator():



        result = answer_question(


            request.question,


            current_user.id,


            db,


            session_id,

            project_id


        )



        answer = result["answer"]




        # 模拟流式输出

        for char in answer:



            data = {


                "content":char

            }



            yield (

                "data: "

                +

                json.dumps(

                    data,

                    ensure_ascii=False

                )

                +

                "\n\n"

            )



            await asyncio.sleep(0.03)





        # 最后发送完整信息

        yield (

            "data: "

            +

            json.dumps(

                {

                    "done":True,

                    "sources":
                        result["sources"],

                    "session_id":
                        result["session_id"]

                },

                ensure_ascii=False

            )

            +

            "\n\n"

        )




    return StreamingResponse(


        event_generator(),


        media_type="text/event-stream"

    )
