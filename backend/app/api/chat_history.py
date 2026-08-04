# 聊天历史接口
# 获取历史会话和历史消息


from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from app.database.connection import get_db

from app.core.dependencies import get_current_user, get_user_project_or_404

from app.models.user import User

from app.models.chat_session import ChatSession

from app.models.chat_message import ChatMessage



router = APIRouter(

    prefix="/chat/history",

    tags=["聊天历史"]

)



# 获取历史会话列表
@router.get("/")
def get_history_list(

    project_id: int | None = None,

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)

):

    if project_id is not None:
        get_user_project_or_404(
            db,
            current_user,
            project_id
        )

    session_query = db.query(ChatSession).filter(

        ChatSession.user_id == current_user.id

    )

    if project_id is not None:
        session_query = session_query.filter(
            ChatSession.project_id == project_id
        )

    sessions = session_query.order_by(

        ChatSession.updated_at.desc()

    ).all()



    return [

        {

            "session_id": item.session_id,

            "title": item.title,

            "project_id": item.project_id,

            "created_at": item.created_at,

            "updated_at": item.updated_at

        }

        for item in sessions

    ]





# 获取某一次聊天详情
@router.get("/{session_id}")
def get_history_detail(

    session_id: str,

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)

):


    messages = db.query(ChatMessage).filter(

        ChatMessage.session_id == session_id,

        ChatMessage.user_id == current_user.id

    ).order_by(

        ChatMessage.created_at.asc()

    ).all()



    return [

        {

            "role": item.role,

            "content": item.content,

            "time": item.created_at

        }

        for item in messages

    ]

# 删除聊天记录

@router.delete("/{session_id}")
def delete_history(

    session_id: str,

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)

):


    # 删除消息

    db.query(ChatMessage).filter(

        ChatMessage.session_id == session_id,

        ChatMessage.user_id == current_user.id

    ).delete()



    # 删除会话

    db.query(ChatSession).filter(

        ChatSession.session_id == session_id,

        ChatSession.user_id == current_user.id

    ).delete()



    db.commit()


    return {

        "message": "删除成功",

        "session_id": session_id

    }
