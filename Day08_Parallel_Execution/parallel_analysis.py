import os
from typing import TypedDict, Annotated
from operator import add
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq

load_dotenv()

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY")
)

# ─────────────────────────────────────────────
# 🧠 State — Annotated[list, add] lets parallel nodes
#            append results without overwriting each other
# ─────────────────────────────────────────────
class AnalysisState(TypedDict):
    topic: str
    results: Annotated[list, add]   # 🔥 accumulates from parallel nodes

# ─────────────────────────────────────────────
# 🔹 Parallel Analysis Nodes
# ─────────────────────────────────────────────

def explain_node(state: AnalysisState) -> dict:
    """Parallel Task 1: Explain the topic"""
    print("🔹 [explain] running...")
    res = llm.invoke(f"Explain '{state['topic']}' in 2 sentences for a beginner.")
    return {"results": [f"📖 EXPLANATION:\n{res.content}"]}

def pros_node(state: AnalysisState) -> dict:
    """Parallel Task 2: List pros"""
    print("🔹 [pros] running...")
    res = llm.invoke(f"List 3 advantages of '{state['topic']}' in bullet points.")
    return {"results": [f"✅ ADVANTAGES:\n{res.content}"]}

def cons_node(state: AnalysisState) -> dict:
    """Parallel Task 3: List cons"""
    print("🔹 [cons] running...")
    res = llm.invoke(f"List 3 disadvantages of '{state['topic']}' in bullet points.")
    return {"results": [f"⚠️  DISADVANTAGES:\n{res.content}"]}

def use_cases_node(state: AnalysisState) -> dict:
    """Parallel Task 4: Real use cases"""
    print("🔹 [use_cases] running...")
    res = llm.invoke(f"Give 3 real-world use cases of '{state['topic']}' in bullet points.")
    return {"results": [f"🌍 USE CASES:\n{res.content}"]}

# ─────────────────────────────────────────────
# 🔹 Merge Node — combines all parallel results
# ─────────────────────────────────────────────

def merge_results(state: AnalysisState) -> AnalysisState:
    """Fan-in: merge all parallel results into final output"""
    print("\n🔀 [merge] combining all results...")
    return state  # results already combined by Annotated[list, add]

# ─────────────────────────────────────────────
# 🔧 Build Graph — Fan-out → Fan-in
# ─────────────────────────────────────────────
builder = StateGraph(AnalysisState)

builder.add_node("start",     lambda x: x)       # pass-through entry
builder.add_node("explain",   explain_node)
builder.add_node("pros",      pros_node)
builder.add_node("cons",      cons_node)
builder.add_node("use_cases", use_cases_node)
builder.add_node("merge",     merge_results)

builder.set_entry_point("start")

# 🔥 Fan-out: start → 4 parallel nodes
builder.add_edge("start",   "explain")
builder.add_edge("start",   "pros")
builder.add_edge("start",   "cons")
builder.add_edge("start",   "use_cases")

# 🔥 Fan-in: all 4 parallel nodes → merge
builder.add_edge("explain",   "merge")
builder.add_edge("pros",      "merge")
builder.add_edge("cons",      "merge")
builder.add_edge("use_cases", "merge")

builder.add_edge("merge", END)

graph = builder.compile()

# ─────────────────────────────────────────────
# 🚀 Run
# ─────────────────────────────────────────────
topic = input("Enter a topic to analyze in parallel: ")

print(f"\n🚀 Running 4 parallel analyses for: '{topic}'\n")

result = graph.invoke({"topic": topic, "results": []})

print("\n" + "="*60)
print(f"📊 FULL ANALYSIS: {topic}")
print("="*60)
for section in result["results"]:
    print(f"\n{section}")
    print("─"*60)
