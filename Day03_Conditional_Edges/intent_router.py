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
# 🧠 State
# ─────────────────────────────────────────────
class IntentState(TypedDict):
    user_input: str
    intent: str
    response: str

# ─────────────────────────────────────────────
# 🔹 Intent Classifier Node
# ─────────────────────────────────────────────
def detect_intent(state: IntentState) -> IntentState:
    response = llm.invoke(
        f"Classify this user message into one of three intents: 'question', 'task', or 'smalltalk'.\n"
        f"Message: {state['user_input']}\n"
        f"Reply with only one word."
    )
    state["intent"] = response.content.strip().lower()
    print(f"🎯 Intent: {state['intent']}")
    return state

# ─────────────────────────────────────────────
# 🔹 Handler Nodes
# ─────────────────────────────────────────────
def handle_question(state: IntentState) -> IntentState:
    response = llm.invoke(f"Answer this question accurately and concisely: {state['user_input']}")
    state["response"] = f"📚 {response.content}"
    return state

def handle_task(state: IntentState) -> IntentState:
    response = llm.invoke(f"Complete this task step by step: {state['user_input']}")
    state["response"] = f"✅ {response.content}"
    return state

def handle_smalltalk(state: IntentState) -> IntentState:
    response = llm.invoke(f"Respond in a friendly, casual way: {state['user_input']}")
    state["response"] = f"💬 {response.content}"
    return state

# ─────────────────────────────────────────────
# 🔀 Router
# ─────────────────────────────────────────────
def route_intent(state: IntentState) -> str:
    if "question" in state["intent"]:
        return "question"
    elif "task" in state["intent"]:
        return "task"
    return "smalltalk"

# ─────────────────────────────────────────────
# 🔧 Build Graph
# ─────────────────────────────────────────────
builder = StateGraph(IntentState)

builder.add_node("detect_intent", detect_intent)
builder.add_node("question_handler", handle_question)
builder.add_node("task_handler", handle_task)
builder.add_node("smalltalk_handler", handle_smalltalk)

builder.set_entry_point("detect_intent")

builder.add_conditional_edges(
    "detect_intent",
    route_intent,
    {
        "question":  "question_handler",
        "task":      "task_handler",
        "smalltalk": "smalltalk_handler"
    }
)

builder.add_edge("question_handler", END)
builder.add_edge("task_handler", END)
builder.add_edge("smalltalk_handler", END)

graph = builder.compile()

# ─────────────────────────────────────────────
# 🚀 Run
# ─────────────────────────────────────────────
print("🤖 Intent-Routing Assistant (type 'bye' to exit)\n")

while True:
    user_input = input("You: ")
    if user_input.lower() == "bye":
        print("Goodbye 👋")
        break

    result = graph.invoke({"user_input": user_input, "intent": "", "response": ""})
    print(f"AI: {result['response']}\n")
