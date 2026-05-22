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
# 🧠 State — includes attempt counter
# ─────────────────────────────────────────────
class QualityState(TypedDict):
    topic: str
    essay: str
    score: int
    feedback: str
    attempts: int
    max_attempts: int

# ─────────────────────────────────────────────
# 🔹 Nodes
# ─────────────────────────────────────────────

def write_essay(state: QualityState) -> QualityState:
    """Generate or improve the essay"""
    state["attempts"] += 1
    print(f"\n✏️  Writing attempt #{state['attempts']}...")

    if state["feedback"]:
        prompt = f"Rewrite and improve this essay based on feedback.\nEssay:\n{state['essay']}\nFeedback: {state['feedback']}\nWrite a better version:"
    else:
        prompt = f"Write a short 3-paragraph essay about: {state['topic']}"

    response = llm.invoke(prompt)
    state["essay"] = response.content
    return state

def evaluate_essay(state: QualityState) -> QualityState:
    """Score the essay from 1-10 and give feedback"""
    response = llm.invoke(
        f"Rate this essay on a scale of 1-10 for quality and clarity.\n"
        f"Essay:\n{state['essay']}\n\n"
        f"Reply in this exact format:\nSCORE: <number>\nFEEDBACK: <one sentence of improvement>"
    )

    lines = response.content.strip().splitlines()
    score_line = next((l for l in lines if l.startswith("SCORE:")), "SCORE: 5")
    feedback_line = next((l for l in lines if l.startswith("FEEDBACK:")), "FEEDBACK: Improve clarity.")

    try:
        state["score"] = int(score_line.replace("SCORE:", "").strip())
    except ValueError:
        state["score"] = 5

    state["feedback"] = feedback_line.replace("FEEDBACK:", "").strip()
    print(f"📊 Score: {state['score']}/10 | Feedback: {state['feedback']}")
    return state

def finalize(state: QualityState) -> QualityState:
    """Final node — essay passed quality check"""
    print(f"\n🏆 Essay approved after {state['attempts']} attempt(s)!")
    return state

# ─────────────────────────────────────────────
# 🔀 Router — exit if score >= 8 or max attempts reached
# ─────────────────────────────────────────────
def quality_router(state: QualityState) -> str:
    if state["score"] >= 8 or state["attempts"] >= state["max_attempts"]:
        return "done"
    return "retry"

# ─────────────────────────────────────────────
# 🔧 Build Graph with Loop
# ─────────────────────────────────────────────
builder = StateGraph(QualityState)

builder.add_node("write", write_essay)
builder.add_node("evaluate", evaluate_essay)
builder.add_node("final", finalize)

builder.set_entry_point("write")
builder.add_edge("write", "evaluate")

# 🔥 Loop: evaluate → retry (back to write) OR done (forward to final)
builder.add_conditional_edges(
    "evaluate",
    quality_router,
    {
        "retry": "write",  # 🔁 loop back
        "done":  "final"   # ✅ exit loop
    }
)

builder.add_edge("final", END)

graph = builder.compile()

# ─────────────────────────────────────────────
# 🚀 Run
# ─────────────────────────────────────────────
topic = input("Enter an essay topic: ")

result = graph.invoke({
    "topic": topic,
    "essay": "",
    "score": 0,
    "feedback": "",
    "attempts": 0,
    "max_attempts": 3
})

print("\n" + "="*50)
print("📄 FINAL ESSAY:")
print("="*50)
print(result["essay"])
print(f"\n✅ Final score: {result['score']}/10 after {result['attempts']} attempt(s)")
