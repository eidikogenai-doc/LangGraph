import os
from typing import TypedDict, Annotated
from operator import add
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

load_dotenv()

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY")
)

# ─────────────────────────────────────────────
# 🧠 State — messages accumulate with 'add' operator
# ─────────────────────────────────────────────
class ChatState(TypedDict):
    messages: Annotated[list, add]

# ─────────────────────────────────────────────
# 🔹 Chat Node
# ─────────────────────────────────────────────

SYSTEM_MESSAGE = SystemMessage(content=(
    "You are a helpful AI assistant. You remember everything the user has told you "
    "in this conversation. Use that context to give personalized, relevant responses."
))

def chat_node(state: ChatState) -> ChatState:
    """Call LLM with full message history"""
    all_messages = [SYSTEM_MESSAGE] + state["messages"]
    response = llm.invoke(all_messages)
    return {"messages": [AIMessage(content=response.content)]}

# ─────────────────────────────────────────────
# 🔧 Build Graph with MemorySaver
# ─────────────────────────────────────────────
builder = StateGraph(ChatState)
builder.add_node("chat", chat_node)
builder.set_entry_point("chat")
builder.add_edge("chat", END)

# 🔥 Compile with checkpointer — enables persistent memory
checkpointer = MemorySaver()
graph = builder.compile(checkpointer=checkpointer)

# ─────────────────────────────────────────────
# 🚀 Multi-user Chat (different thread_id = different memory)
# ─────────────────────────────────────────────
print("🤖 Memory-Enabled Chatbot")
print("💡 Each session_id has its own independent memory.\n")

session_id = input("Enter your session ID (e.g. alice, bob, user1): ").strip() or "default"
config = {"configurable": {"thread_id": session_id}}

print(f"\n✅ Session '{session_id}' started. Type 'bye' to exit.\n")

while True:
    user_input = input("You: ").strip()
    if user_input.lower() == "bye":
        print("AI: Goodbye! I'll remember our conversation. 👋")
        break

    result = graph.invoke(
        {"messages": [HumanMessage(content=user_input)]},
        config=config
    )

    # Get last AI message
    ai_messages = [m for m in result["messages"] if isinstance(m, AIMessage)]
    print(f"AI: {ai_messages[-1].content}\n")
