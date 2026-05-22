import os
from typing import TypedDict
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq

load_dotenv()

# streaming=True on LLM for token-level output inside nodes
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY"),
    streaming=True
)

# ─────────────────────────────────────────────
# 🧠 State
# ─────────────────────────────────────────────
class StreamState(TypedDict):
    input: str
    explanation: str
    summary: str
    formatted: str

# ─────────────────────────────────────────────
# 🔹 Nodes — each streams LLM output live
# ─────────────────────────────────────────────

def explain_node(state: StreamState) -> StreamState:
    """Node 1: Explain the topic with streaming"""
    print("\n🔹 [Node: explain]")
    full_text = ""
    for chunk in llm.stream(f"Explain this in 3 sentences: {state['input']}"):
        print(chunk.content, end="", flush=True)
        full_text += chunk.content
    print("\n")
    state["explanation"] = full_text
    return state

def summarize_node(state: StreamState) -> StreamState:
    """Node 2: Summarize the explanation with streaming"""
    print("\n🔹 [Node: summarize]")
    full_text = ""
    for chunk in llm.stream(f"Summarize in one sentence:\n{state['explanation']}"):
        print(chunk.content, end="", flush=True)
        full_text += chunk.content
    print("\n")
    state["summary"] = full_text
    return state

def format_node(state: StreamState) -> StreamState:
    """Node 3: Format the final output"""
    print("\n🔹 [Node: format]")
    state["formatted"] = (
        f"\n{'='*50}\n"
        f"📖 Topic: {state['input']}\n"
        f"{'─'*50}\n"
        f"📚 Explanation:\n{state['explanation']}\n"
        f"{'─'*50}\n"
        f"📌 Summary: {state['summary']}\n"
        f"{'='*50}"
    )
    return state

# ─────────────────────────────────────────────
# 🔧 Build Graph
# ─────────────────────────────────────────────
builder = StateGraph(StreamState)

builder.add_node("explain", explain_node)
builder.add_node("summarize", summarize_node)
builder.add_node("format", format_node)

builder.set_entry_point("explain")
builder.add_edge("explain", "summarize")
builder.add_edge("summarize", "format")
builder.add_edge("format", END)

graph = builder.compile()

# ─────────────────────────────────────────────
# 🚀 Run with Graph-level Streaming
# ─────────────────────────────────────────────
user_input = input("Enter a topic to explain: ")
print(f"\n🚀 Starting streaming graph for: '{user_input}'\n")

# graph.stream() shows each node as it completes
for step in graph.stream({
    "input": user_input,
    "explanation": "",
    "summary": "",
    "formatted": ""
}):
    node_name = list(step.keys())[0]
    print(f"\n✅ Node '{node_name}' completed.")

print("\n📊 FINAL OUTPUT:")
# Get the final result via invoke for clean access
result = graph.invoke({
    "input": user_input,
    "explanation": "",
    "summary": "",
    "formatted": ""
})
print(result["formatted"])
