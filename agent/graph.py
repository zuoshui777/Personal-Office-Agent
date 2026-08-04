# LangGraph 多 Agent 编排图

from langgraph.graph import StateGraph, END

from agent.state import AgentState
from agent.router_agent import route_user_input
from agent.knowledge_agent import run_knowledge_agent
from agent.browser_agent import run_browser_agent
from agent.document_agent import run_document_agent
from agent.workflow_agent import run_workflow_agent


def router_node(state: AgentState):
    return {
        **state,
        "task_type": route_user_input(state["user_input"])
    }


def knowledge_node(state: AgentState):
    result = run_knowledge_agent(
        state["user_input"],
        state.get("project_id"),
        state.get("history", []),
        state.get("memories", [])
    )
    return {
        **state,
        "retrieved_docs": result.get("sources", []),
        "final_answer": result["answer"]
    }


def browser_node(state: AgentState):
    result = run_browser_agent(
        state["user_input"],
        state.get("history", []),
        state.get("memories", [])
    )
    return {
        **state,
        "tool_result": result.get("tool_result", ""),
        "final_answer": result["answer"]
    }


def document_node(state: AgentState):
    question = state["user_input"].lower()
    doc_type = (
        "ppt" if "ppt" in question
        else "excel" if "excel" in question
        else "word"
    )
    result = run_document_agent(state["user_input"], doc_type=doc_type)
    return {
        **state,
        "tool_result": result.get("tool_result", ""),
        "final_answer": result["answer"]
    }


def workflow_node(state: AgentState):
    result = run_workflow_agent(
        state["user_input"],
        state.get("project_id"),
        state.get("history", []),
        state.get("memories", [])
    )
    return {
        **state,
        "tool_result": result.get("tool_result", ""),
        "retrieved_docs": result.get("sources", []),
        "final_answer": result["answer"]
    }


builder = StateGraph(AgentState)
builder.add_node("router", router_node)
builder.add_node("knowledge", knowledge_node)
builder.add_node("browser", browser_node)
builder.add_node("document", document_node)
builder.add_node("workflow", workflow_node)

builder.set_entry_point("router")
builder.add_conditional_edges(
    "router",
    lambda state: state["task_type"],
    {
        "knowledge": "knowledge",
        "browser": "browser",
        "document": "document",
        "workflow": "workflow"
    }
)

for node in ("knowledge", "browser", "document", "workflow"):
    builder.add_edge(node, END)

agent_graph = builder.compile()
