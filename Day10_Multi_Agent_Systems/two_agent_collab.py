import os
from typing import TypedDict, Annotated
from operator import add
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

load_dotenv()

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY")
)

# ─────────────────────────────────────────────
# 🧠 State
# ─────────────────────────────────────────────
class CollabState(TypedDict):
    topic: str
    plan: str
    content: str
    review: str
    approved: bool

# ─────────────────────────────────────────────
# 🔹 Agent Nodes — 2-agent pipeline
# ─────────────────────────────────────────────

def planner_agent(state: CollabState) -> CollabState:
    """Agent 1: Creates a structured plan"""
    print("\n🗺️  [Planner Agent] creating plan...")
    response = llm.invoke([
        SystemMessage("You are a strategic planner. Create a clear, concise 3-point plan."),
        HumanMessage(content=f"Create a plan for: {state['topic']}")
    ])
    state["plan"] = response.content
    print("  ✅ Plan ready.")
    return state

def creator_agent(state: CollabState) -> CollabState:
    """Agent 2: Creates content based on the plan"""
    print("\n🎨 [Creator Agent] creating content...")
    response = llm.invoke([
        SystemMessage("You are a creative content creator. Execute the plan and create engaging content."),
        HumanMessage(content=f"Topic: {state['topic']}\n\nPlan to execute:\n{state['plan']}\n\nCreate the content:")
    ])
    state["content"] = response.content
    print("  ✅ Content ready.")
    return state

def reviewer_agent(state: CollabState) -> CollabState:
    """Agent 3: Reviews the final output"""
    print("\n🔍 [Reviewer Agent] reviewing...")
    response = llm.invoke([
        SystemMessage(
            "You are a quality reviewer. Review the content against the plan. "
            "End your review with either 'APPROVED' or 'NEEDS_REVISION'."
        ),
        HumanMessage(
            content=(
                f"Original topic: {state['topic']}\n\n"
                f"Plan:\n{state['plan']}\n\n"
                f"Content:\n{state['content']}\n\n"
                f"Does the content match the plan and meet quality standards?"
            )
        )
    ])
    state["review"] = response.content
    state["approved"] = "APPROVED" in response.content.upper()
    status = "✅ APPROVED" if state["approved"] else "⚠️  NEEDS REVISION"
    print(f"  {status}")
    return state

# ─────────────────────────────────────────────
# 🔀 Router
# ─────────────────────────────────────────────
def review_router(state: CollabState) -> str:
    return "done" if state["approved"] else "revise"

# ─────────────────────────────────────────────
# 🔧 Build Graph
# ─────────────────────────────────────────────
builder = StateGraph(CollabState)

builder.add_node("planner",  planner_agent)
builder.add_node("creator",  creator_agent)
builder.add_node("reviewer", reviewer_agent)

builder.set_entry_point("planner")
builder.add_edge("planner", "creator")
builder.add_edge("creator", "reviewer")

builder.add_conditional_edges(
    "reviewer",
    review_router,
    {
        "done":   END,
        "revise": "creator"   # 🔁 loop: revise if not approved
    }
)

graph = builder.compile()

# ─────────────────────────────────────────────
# 🚀 Run
# ─────────────────────────────────────────────
print("🤖 2-Agent Collaboration: Planner → Creator → Reviewer\n")

topic = input("Enter a topic for the agents to work on: ")

result = graph.invoke({
    "topic": topic,
    "plan": "",
    "content": "",
    "review": "",
    "approved": False
})

print("\n" + "="*60)
print("📋 PLAN:")
print("─"*60)
print(result["plan"])
print("\n" + "="*60)
print("📄 FINAL CONTENT:")
print("─"*60)
print(result["content"])
