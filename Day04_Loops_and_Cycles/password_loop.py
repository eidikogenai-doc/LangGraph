from langgraph.graph import StateGraph, END
from typing import TypedDict

# ─────────────────────────────────────────────
# 🧠 State
# ─────────────────────────────────────────────
class PasswordState(TypedDict):
    password: str
    attempts: int
    authenticated: bool

# ─────────────────────────────────────────────
# 🔹 Nodes
# ─────────────────────────────────────────────

def ask_password(state: PasswordState) -> PasswordState:
    """Ask user for password"""
    state["attempts"] += 1
    state["password"] = input(f"\n🔒 Enter password (attempt {state['attempts']}): ")
    return state

def check_password(state: PasswordState) -> PasswordState:
    """Verify password"""
    if state["password"] == "langgraph123":
        state["authenticated"] = True
        print("✅ Password correct!")
    else:
        state["authenticated"] = False
        print("❌ Wrong password!")
    return state

def welcome(state: PasswordState) -> PasswordState:
    """Welcome authenticated user"""
    print(f"\n🎉 Welcome! You authenticated on attempt #{state['attempts']}.")
    return state

def locked_out(state: PasswordState) -> PasswordState:
    """Too many failed attempts"""
    print(f"\n🚫 Too many failed attempts. Account locked.")
    return state

# ─────────────────────────────────────────────
# 🔀 Router
# ─────────────────────────────────────────────
def auth_router(state: PasswordState) -> str:
    if state["authenticated"]:
        return "success"
    elif state["attempts"] >= 3:
        return "locked"
    return "retry"

# ─────────────────────────────────────────────
# 🔧 Build Graph
# ─────────────────────────────────────────────
builder = StateGraph(PasswordState)

builder.add_node("ask", ask_password)
builder.add_node("check", check_password)
builder.add_node("welcome", welcome)
builder.add_node("locked_out", locked_out)

builder.set_entry_point("ask")
builder.add_edge("ask", "check")

# 🔥 Loop: retry → back to ask | success/locked → forward
builder.add_conditional_edges(
    "check",
    auth_router,
    {
        "retry":   "ask",         # 🔁 loop back
        "success": "welcome",     # ✅ exit
        "locked":  "locked_out"   # 🚫 exit
    }
)

builder.add_edge("welcome", END)
builder.add_edge("locked_out", END)

graph = builder.compile()

# ─────────────────────────────────────────────
# 🚀 Run  (correct password: langgraph123)
# ─────────────────────────────────────────────
print("🔐 Login System (correct password: langgraph123)\n")
graph.invoke({"password": "", "attempts": 0, "authenticated": False})
