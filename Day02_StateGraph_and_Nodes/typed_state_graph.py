import os
from typing import TypedDict
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq

load_dotenv()

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY")
)

# ─────────────────────────────────────────────
# 🧠 Typed State — defines all fields in shared state
# ─────────────────────────────────────────────
class BlogState(TypedDict):
    topic: str
    outline: str
    draft: str
    final: str

# ─────────────────────────────────────────────
# 🔹 Nodes — each is a pure function
# ─────────────────────────────────────────────

def create_outline(state: BlogState) -> BlogState:
    """Node 1: Create a blog outline from the topic"""
    response = llm.invoke(f"Create a short 3-point outline for a blog post about: {state['topic']}")
    state["outline"] = response.content
    print("✅ Outline created")
    return state

def write_draft(state: BlogState) -> BlogState:
    """Node 2: Write a blog draft from the outline"""
    response = llm.invoke(
        f"Write a short blog post (200 words) based on this outline:\n{state['outline']}"
    )
    state["draft"] = response.content
    print("✅ Draft written")
    return state

def polish_draft(state: BlogState) -> BlogState:
    """Node 3: Polish the draft for grammar and clarity"""
    response = llm.invoke(
        f"Polish this blog post — improve grammar and flow, keep it under 250 words:\n{state['draft']}"
    )
    state["final"] = response.content
    print("✅ Draft polished")
    return state

# ─────────────────────────────────────────────
# 🔧 Build the Sequential Graph
# ─────────────────────────────────────────────
builder = StateGraph(BlogState)

builder.add_node("create_outline", create_outline)
builder.add_node("write_draft", write_draft)
builder.add_node("polish_draft", polish_draft)

# Set entry point
builder.set_entry_point("create_outline")

# Connect nodes: outline → draft → polish → END
builder.add_edge("create_outline", "write_draft")
builder.add_edge("write_draft", "polish_draft")
builder.add_edge("polish_draft", END)

graph = builder.compile()

# ─────────────────────────────────────────────
# 🚀 Run
# ─────────────────────────────────────────────
topic = input("Enter a blog topic: ")

print(f"\n🚀 Running blog writer graph for: '{topic}'\n")

result = graph.invoke({"topic": topic, "outline": "", "draft": "", "final": ""})

print("\n" + "="*50)
print("📄 FINAL BLOG POST:")
print("="*50)
print(result["final"])
