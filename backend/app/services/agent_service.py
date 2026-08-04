# Agent 调度服务

from agent.graph import agent_graph

from app.services.chat_history_service import get_chat_history
from app.services.memory_service import (
    extract_and_save_memories,
    get_memories
)


def run_agent(
    question: str,
    user_id: int,
    db,
    project_id: int | None = None,
    history: list | None = None,
    memories: list | None = None
):
    if history is None:
        history = get_chat_history(db, session_id="")
    if memories is None:
        memories = get_memories(db, user_id)

    extract_and_save_memories(db, user_id, question)

    state = agent_graph.invoke(
        {
            "user_input": question,
            "task_type": "knowledge",
            "project_id": project_id,
            "retrieved_docs": [],
            "need_web": False,
            "tool_result": "",
            "final_answer": "",
            "memories": memories,
            "history": history
        }
    )

    return {
        "answer": state.get("final_answer", ""),
        "sources": state.get("retrieved_docs", []),
        "tool_result": state.get("tool_result", "")
    }
