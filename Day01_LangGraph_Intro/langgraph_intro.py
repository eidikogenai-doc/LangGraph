import os
from dotenv import load_dotenv
from langgraph.graph import StateGraph
from langchain_groq import ChatGroq

# 🔑 Load API key
load_dotenv()

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY")
)

# ─────────────────────────────────────────────
# 🧠 What is a Node?
# A plain Python function that receives state (dict),
# modifies it, and returns the updated state.
# ─────────────────────────────────────────────

# Node 1 — Ask the LLM a question
def ask_llm(state):
    response = llm.invoke(f"Answer briefly: {state['question']}")
    state["answer"] = response.content
    return state

# Node 2 — Format the output nicely
def format_output(state):
    state["result"] = f"✅ Q: {state['question']}\n💬 A: {state['answer']}"
    return state

# ─────────────────────────────────────────────
# 🔧 Build the Graph
# ─────────────────────────────────────────────
builder = StateGraph(dict)

builder.add_node("ask_llm", ask_llm)
builder.add_node("format_output", format_output)

# Set the starting node
builder.set_entry_point("ask_llm")

# Connect nodes with edges
builder.add_edge("ask_llm", "format_output")

# Compile — locks the graph into a runnable object
graph = builder.compile()

# ─────────────────────────────────────────────
# 🚀 Run the Graph
# ─────────────────────────────────────────────
result = graph.invoke({"question": "What is LangGraph and why is it useful?"})

print(result["result"])
