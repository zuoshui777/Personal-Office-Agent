from typing import TypedDict


class AgentState(TypedDict):
    user_input: str
    task_type: str
    project_id: int | None
    retrieved_docs: list
    need_web: bool
    tool_result: str
    final_answer: str
    memories: list
    history: list
