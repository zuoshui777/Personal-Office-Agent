# 智能问答业务服务

from datetime import datetime

from app.services.chat_history_service import get_chat_history
from app.services.agent_service import run_agent
from app.models.chat_message import ChatMessage
from app.models.chat_session import ChatSession


def answer_question(
    question: str,
    user_id: int,
    db,
    session_id: str,
    project_id: int | None = None
):
    session = (
        db.query(ChatSession)
        .filter(ChatSession.session_id == session_id)
        .first()
    )

    if session is None:
        session = ChatSession(
            session_id=session_id,
            user_id=user_id,
            project_id=project_id,
            title=question[:20]
        )
        db.add(session)
        db.commit()

    if project_id is not None and session.project_id is None:
        session.project_id = project_id

    history = get_chat_history(db, session_id)

    result = run_agent(
        question=question,
        user_id=user_id,
        db=db,
        project_id=project_id,
        history=history
    )

    db.add(
        ChatMessage(
            user_id=user_id,
            session_id=session_id,
            role="user",
            content=question
        )
    )
    db.add(
        ChatMessage(
            user_id=user_id,
            session_id=session_id,
            role="assistant",
            content=result["answer"]
        )
    )
    session.updated_at = datetime.utcnow()
    db.commit()

    return {
        "answer": result["answer"],
        "sources": result.get("sources", []),
        "session_id": session_id
    }
