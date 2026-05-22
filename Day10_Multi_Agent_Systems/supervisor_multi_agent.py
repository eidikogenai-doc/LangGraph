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
# 🧠 Shared State
# ─────────────────────────────────────────────
class MultiAgentState(TypedDict):
    messages: Annotated[list, add]
    next_agent: str
    iteration: int

# ─────────────────────────────────────────────
# 🔹 Subagent Nodes
# ─────────────────────────────────────────────

def researcher_agent(state: MultiAgentState) -> dict:
    """Subagent 1: Finds facts and information"""
    print("\n🔬 [Researcher Agent] working...")

    response = llm.invoke([
        SystemMessage(
            "You are an expert researcher. Given a user request, find and present "
            "the key facts, data points, and background information concisely. "
            "Start your response with '🔬 [Research]:'"
        ),
        HumanMessage(content=state["messages"][0].content)
    ])

    print(f"  → Research complete.")
    return {
        "messages": [AIMessage(content=response.content)],
        "iteration": state["iteration"] + 1
    }


def writer_agent(state: MultiAgentState) -> dict:
    """Subagent 2: Writes content based on research"""
    print("\n✍️  [Writer Agent] working...")

    # Get research results from message history
    research = next(
        (m.content for m in state["messages"] if "🔬 [Research]" in m.content),
        "No research available."
    )

    response = llm.invoke([
        SystemMessage(
            "You are an expert content writer. Using the research provided, "
            "write a clear, engaging, well-structured response for the user. "
            "Start your response with '✍️ [Written Content]:'"
        ),
        HumanMessage(
            content=f"User's request: {state['messages'][0].content}\n\nResearch findings:\n{research}"
        )
    ])

    print("  → Writing complete.")
    return {
        "messages": [AIMessage(content=response.content)],
        "iteration": state["iteration"] + 1
    }


def editor_agent(state: MultiAgentState) -> dict:
    """Subagent 3: Polishes and finalizes the content"""
    print("\n📝 [Editor Agent] working...")

    # Get latest written content
    written = next(
        (m.content for m in reversed(state["messages"]) if "✍️ [Written Content]" in m.content),
        state["messages"][-1].content
    )

    response = llm.invoke([
        SystemMessage(
            "You are a professional editor. Polish the content for clarity, "
            "grammar, and flow. Make it ready for the user. "
            "Present the FINAL polished version without any labels."
        ),
        HumanMessage(content=f"Polish this:\n{written}")
    ])

    print("  → Editing complete.")
    return {
        "messages": [AIMessage(content=response.content)],
        "iteration": state["iteration"] + 1
    }


def supervisor_agent(state: MultiAgentState) -> dict:
    """Supervisor: Decides which agent to call next or if we're done"""
    print(f"\n🎯 [Supervisor] deciding... (iteration {state['iteration']})")

    agents_used = []
    for m in state["messages"]:
        if isinstance(m, AIMessage):
            if "🔬 [Research]" in m.content:
                agents_used.append("researcher")
            elif "✍️ [Written Content]" in m.content:
                agents_used.append("writer")

    # Routing logic
    if "researcher" not in agents_used:
        decision = "researcher"
    elif "writer" not in agents_used:
        decision = "writer"
    elif state["iteration"] < 6:
        decision = "editor"
    else:
        decision = "FINISH"

    print(f"  → Routing to: {decision}")
    return {"next_agent": decision, "messages": []}


# ─────────────────────────────────────────────
# 🔀 Router
# ─────────────────────────────────────────────
def route_from_supervisor(state: MultiAgentState) -> str:
    return state["next_agent"]


# ─────────────────────────────────────────────
# 🔧 Build Multi-Agent Graph
# ─────────────────────────────────────────────
builder = StateGraph(MultiAgentState)

builder.add_node("supervisor",  supervisor_agent)
builder.add_node("researcher",  researcher_agent)
builder.add_node("writer",      writer_agent)
builder.add_node("editor",      editor_agent)

builder.set_entry_point("supervisor")

# Supervisor routes to the right agent
builder.add_conditional_edges(
    "supervisor",
    route_from_supervisor,
    {
        "researcher": "researcher",
        "writer":     "writer",
        "editor":     "editor",
        "FINISH":     END
    }
)

# All subagents report back to supervisor
builder.add_edge("researcher", "supervisor")
builder.add_edge("writer",     "supervisor")
builder.add_edge("editor",     "supervisor")

graph = builder.compile()

# ─────────────────────────────────────────────
# 🚀 Run
# ─────────────────────────────────────────────
print("🤖 Multi-Agent System: Supervisor + Researcher + Writer + Editor\n")

task = input("Enter your task (e.g. 'Write a blog post about LangGraph'): ")

print(f"\n🚀 Starting multi-agent pipeline for: '{task}'\n")

result = graph.invoke({
    "messages": [HumanMessage(content=task)],
    "next_agent": "",
    "iteration": 0
})

# Show final output (last AIMessage that's not labeled)
print("\n" + "="*60)
print("📄 FINAL OUTPUT:")
print("="*60)
for msg in reversed(result["messages"]):
    if isinstance(msg, AIMessage) and msg.content:
        print(msg.content)
        break
