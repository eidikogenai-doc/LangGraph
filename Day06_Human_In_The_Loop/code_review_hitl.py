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
class CodeReviewState(TypedDict):
    requirement: str
    code: str
    review_notes: str
    decision: str  # "approve" | "request_changes" | "reject"
    revision: int

# ─────────────────────────────────────────────
# 🔹 Nodes
# ─────────────────────────────────────────────

def generate_code(state: CodeReviewState) -> CodeReviewState:
    """AI generates Python code"""
    state["revision"] += 1
    print(f"\n⚙️  Generating code (revision #{state['revision']})...")

    if state["review_notes"]:
        prompt = (
            f"Revise this Python code based on the review notes.\n\n"
            f"Code:\n```python\n{state['code']}\n```\n\n"
            f"Review notes: {state['review_notes']}\n\n"
            f"Provide only the revised code, no explanation:"
        )
    else:
        prompt = (
            f"Write clean, working Python code for: {state['requirement']}\n"
            f"Include docstrings and comments. Provide only code, no explanation."
        )

    response = llm.invoke(prompt)
    state["code"] = response.content
    state["review_notes"] = ""
    return state

def human_code_review(state: CodeReviewState) -> CodeReviewState:
    """⏸️  Human reviews the generated code"""
    print("\n" + "─"*55)
    print(f"💻 GENERATED CODE (Revision #{state['revision']}):")
    print("─"*55)
    print(state["code"])
    print("─"*55)

    print("\nOptions: approve / request_changes / reject")
    decision = input("Your decision: ").strip().lower()

    if decision not in ("approve", "request_changes", "reject"):
        decision = "request_changes"

    state["decision"] = decision

    if decision == "request_changes":
        notes = input("📝 Enter review notes for the AI: ").strip()
        state["review_notes"] = notes

    return state

def deploy_code(state: CodeReviewState) -> CodeReviewState:
    """Code approved — deploy"""
    print(f"\n🚀 Code approved and deployed after {state['revision']} revision(s)!")
    return state

def reject_code(state: CodeReviewState) -> CodeReviewState:
    """Code rejected"""
    print("\n🚫 Code rejected. Requirement discarded.")
    return state

# ─────────────────────────────────────────────
# 🔀 Router
# ─────────────────────────────────────────────
def review_router(state: CodeReviewState) -> str:
    return state["decision"]

# ─────────────────────────────────────────────
# 🔧 Build Graph
# ─────────────────────────────────────────────
builder = StateGraph(CodeReviewState)

builder.add_node("generate", generate_code)
builder.add_node("review", human_code_review)
builder.add_node("deploy", deploy_code)
builder.add_node("reject", reject_code)

builder.set_entry_point("generate")
builder.add_edge("generate", "review")

builder.add_conditional_edges(
    "review",
    review_router,
    {
        "approve":          "deploy",
        "request_changes":  "generate",  # 🔁 loop
        "reject":           "reject"
    }
)

builder.add_edge("deploy", END)
builder.add_edge("reject", END)

graph = builder.compile()

# ─────────────────────────────────────────────
# 🚀 Run
# ─────────────────────────────────────────────
print("💻 AI Code Generator with Human Review\n")
requirement = input("Describe the code you need: ")

graph.invoke({
    "requirement": requirement,
    "code": "",
    "review_notes": "",
    "decision": "",
    "revision": 0
})
