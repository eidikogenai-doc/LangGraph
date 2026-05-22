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
class EmailState(TypedDict):
    topic: str
    draft: str
    feedback: str
    approved: str
    iteration: int

# ─────────────────────────────────────────────
# 🔹 Nodes
# ─────────────────────────────────────────────

def generate_draft(state: EmailState) -> EmailState:
    """AI generates or improves the email draft"""
    state["iteration"] += 1
    print(f"\n✏️  Generating draft #{state['iteration']}...")

    if state["feedback"]:
        prompt = (
            f"Improve this professional email based on the feedback.\n\n"
            f"Original email:\n{state['draft']}\n\n"
            f"Feedback: {state['feedback']}\n\n"
            f"Write an improved version:"
        )
    else:
        prompt = f"Write a concise, professional email for this purpose: {state['topic']}"

    response = llm.invoke(prompt)
    state["draft"] = response.content
    state["feedback"] = ""  # clear old feedback
    return state

def human_review(state: EmailState) -> EmailState:
    """⏸️  Pause — show draft to human, get their decision"""
    print("\n" + "─"*50)
    print("📧 AI DRAFT EMAIL:")
    print("─"*50)
    print(state["draft"])
    print("─"*50)

    approval = input("\n✅ Approve this email? (yes/no): ").strip().lower()
    state["approved"] = approval

    if approval == "no":
        feedback = input("📝 What should be improved?: ").strip()
        state["feedback"] = feedback

    return state

def send_email(state: EmailState) -> EmailState:
    """Final node — email approved and 'sent'"""
    print(f"\n🚀 Email approved and sent after {state['iteration']} iteration(s)!")
    print("\n📨 FINAL EMAIL SENT:")
    print("─"*50)
    print(state["draft"])
    return state

# ─────────────────────────────────────────────
# 🔀 Router
# ─────────────────────────────────────────────
def review_decision(state: EmailState) -> str:
    return "approve" if state["approved"] == "yes" else "improve"

# ─────────────────────────────────────────────
# 🔧 Build Graph
# ─────────────────────────────────────────────
builder = StateGraph(EmailState)

builder.add_node("generate_draft", generate_draft)
builder.add_node("human_review", human_review)
builder.add_node("send_email", send_email)

builder.set_entry_point("generate_draft")
builder.add_edge("generate_draft", "human_review")

builder.add_conditional_edges(
    "human_review",
    review_decision,
    {
        "approve": "send_email",      # ✅ approved
        "improve": "generate_draft"   # 🔁 loop back for improvement
    }
)

builder.add_edge("send_email", END)

graph = builder.compile()

# ─────────────────────────────────────────────
# 🚀 Run
# ─────────────────────────────────────────────
print("📧 AI Email Drafter with Human Approval\n")
topic = input("Enter email purpose/topic: ")

graph.invoke({
    "topic": topic,
    "draft": "",
    "feedback": "",
    "approved": "",
    "iteration": 0
})
