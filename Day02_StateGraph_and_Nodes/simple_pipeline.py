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
# 🧠 Simple 3-node pipeline: input → process → output
# ─────────────────────────────────────────────

class PipelineState(TypedDict):
    raw_input: str
    cleaned_input: str
    llm_response: str
    formatted_output: str

# Node 1: Clean the input
def clean_input(state: PipelineState) -> PipelineState:
    cleaned = state["raw_input"].strip().lower()
    state["cleaned_input"] = cleaned
    return state

# Node 2: Call LLM
def call_llm(state: PipelineState) -> PipelineState:
    response = llm.invoke(state["cleaned_input"])
    state["llm_response"] = response.content
    return state

# Node 3: Format output
def format_output(state: PipelineState) -> PipelineState:
    state["formatted_output"] = (
        f"\n{'─'*40}\n"
        f"📥 Input:  {state['raw_input']}\n"
        f"🤖 Answer: {state['llm_response']}\n"
        f"{'─'*40}"
    )
    return state

# ─────────────────────────────────────────────
# 🔧 Build Graph
# ─────────────────────────────────────────────
builder = StateGraph(PipelineState)

builder.add_node("clean_input", clean_input)
builder.add_node("call_llm", call_llm)
builder.add_node("format_output", format_output)

builder.set_entry_point("clean_input")
builder.add_edge("clean_input", "call_llm")
builder.add_edge("call_llm", "format_output")
builder.add_edge("format_output", END)

graph = builder.compile()

# ─────────────────────────────────────────────
# 🚀 Run
# ─────────────────────────────────────────────
while True:
    user_input = input("\nYou (type 'bye' to quit): ")
    if user_input.lower() == "bye":
        print("Goodbye 👋")
        break

    result = graph.invoke({
        "raw_input": user_input,
        "cleaned_input": "",
        "llm_response": "",
        "formatted_output": ""
    })
    print(result["formatted_output"])
