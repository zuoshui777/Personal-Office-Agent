# Workflow Agent
# 将复合任务拆成多步并调用对应 Agent

from agent.browser_agent import run_browser_agent
from agent.document_agent import run_document_agent
from agent.knowledge_agent import run_knowledge_agent


def run_workflow_agent(
    question: str,
    project_id: int | None,
    history: list,
    memories: list
):
    steps = []

    if "ppt" in question.lower() or "答辩" in question:
        knowledge = run_knowledge_agent(question, project_id, history, memories, limit=3)
        steps.append({"step": "知识检索", "result": "完成"})
        document = run_document_agent(knowledge["answer"], doc_type="ppt")
        steps.append({"step": "生成PPT", "result": document["tool_result"]})
        return {
            "answer": f"工作流已完成。\n\n{knowledge['answer']}\n\n生成文件：{document['tool_result']}",
            "sources": knowledge["sources"] + document["sources"],
            "tool_result": "\n".join(f"{s['step']}: {s['result']}" for s in steps)
        }

    if any(word in question.lower() for word in ("联网", "搜索", "最新")):
        result = run_browser_agent(question, history, memories)
        return {
            "answer": result["answer"],
            "sources": result["sources"],
            "tool_result": result["tool_result"]
        }

    return run_knowledge_agent(question, project_id, history, memories)
