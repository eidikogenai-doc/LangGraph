# 🦜 LangGraph Learning Journal — Complete 10-Day Course

> **Your personal, organized LangGraph learning path** — built with the exact same structure as your LangChain course, upgraded with full LangGraph code and detailed notes.

---

## 📁 Folder Structure

```
LangGraph-main/
│
├── Day01_LangGraph_Intro/             ← What is LangGraph? Big picture + setup
│   ├── notes.md
│   └── langgraph_intro.py
│
├── Day02_StateGraph_and_Nodes/        ← TypedDict State, Nodes, sequential graphs
│   ├── simple_pipeline.py
│   ├── typed_state_graph.py
│   └── notes.md
│
├── Day03_Conditional_Edges/           ← Routing, branching, smart decision nodes
│   ├── sentiment_router.py
│   ├── intent_router.py
│   └── notes.md
│
├── Day04_Loops_and_Cycles/            ← Retry loops, feedback cycles, quality gates
│   ├── quality_loop.py
│   ├── password_loop.py
│   └── notes.md
│
├── Day05_Memory_and_Checkpointing/    ← MemorySaver, JSON persistence, thread_id
│   ├── memory_saver_chatbot.py
│   ├── json_memory_chatbot.py
│   └── notes.md
│
├── Day06_Human_In_The_Loop/           ← Approval workflows, HITL patterns
│   ├── email_approval.py
│   ├── code_review_hitl.py
│   └── notes.md
│
├── Day07_Streaming/                   ← Token streaming, graph node streaming
│   ├── llm_streaming.py
│   ├── graph_streaming.py
│   └── notes.md
│
├── Day08_Parallel_Execution/          ← Fan-out / Fan-in, Annotated reducers
│   ├── parallel_analysis.py
│   ├── parallel_translation.py
│   └── notes.md
│
├── Day09_ReAct_Agents_and_Tools/      ← @tool, bind_tools, ReAct loop in graphs
│   ├── react_agent.py
│   ├── multi_tool_agent.py
│   └── notes.md
│
└── Day10_Multi_Agent_Systems/         ← Supervisor + subagents, multi-agent orchestration
    ├── supervisor_multi_agent.py
    ├── two_agent_collab.py
    └── notes.md
```

---

## 🗺️ Learning Roadmap

| Day | Topic | Key Concepts | Files |
|-----|-------|-------------|-------|
| 1 | **LangGraph Intro** | StateGraph, Nodes, Edges, compile(), invoke() | 1 file |
| 2 | **StateGraph & Nodes** | TypedDict, sequential pipeline, add_edge | 2 files |
| 3 | **Conditional Edges** | add_conditional_edges, router functions, branching | 2 files |
| 4 | **Loops & Cycles** | Back-edges, retry loops, iteration counter | 2 files |
| 5 | **Memory & Checkpointing** | MemorySaver, thread_id, JSON persistence | 2 files |
| 6 | **Human-in-the-Loop** | Approval workflows, HITL patterns, feedback loops | 2 files |
| 7 | **Streaming** | llm.stream(), graph.stream(), flush=True | 2 files |
| 8 | **Parallel Execution** | Fan-out/fan-in, Annotated[list, add] reducer | 2 files |
| 9 | **ReAct Agents & Tools** | @tool, bind_tools, tool_calls, ToolMessage | 2 files |
| 10 | **Multi-Agent Systems** | Supervisor, subagents, routing, orchestration | 2 files |

---

## 🔑 Key Libraries Used

```
langgraph               — StateGraph, MemorySaver, END
langchain-core          — HumanMessage, AIMessage, ToolMessage, @tool
langchain-groq          — ChatGroq (fast LLM inference)
python-dotenv           — Load GROQ_API_KEY from .env
requests                — HTTP calls (weather API)
```

---

## ⚙️ Setup

1. Install dependencies:
```bash
pip install langgraph langchain-core langchain-groq python-dotenv requests
```

2. Create `.env` file:
```
GROQ_API_KEY=your_groq_api_key_here
WEATHER_API_KEY=your_weather_api_key_here   # optional, for Day 9
```

3. Get your free Groq API key at: https://console.groq.com

---

## 🧱 LangGraph Core Architecture

```
Your Input (initial state)
          ↓
    [Entry Node]        ← set_entry_point("node_name")
          ↓
    [Node 2]            ← add_edge("entry", "node2")
          ↓  ← conditional edge?
   ┌──────┴──────┐
   ↓             ↓
[Path A]     [Path B]   ← add_conditional_edges(...)
   ↓             ↓
  [END]        [loop back]  ← add_edge("path_b", "entry")
```

---

## 🚀 Quick Reference — Most Used Patterns

### Basic Graph
```python
from langgraph.graph import StateGraph, END
from typing import TypedDict

class MyState(TypedDict):
    input: str
    result: str

def my_node(state):
    state["result"] = "processed"
    return state

builder = StateGraph(MyState)
builder.add_node("process", my_node)
builder.set_entry_point("process")
builder.add_edge("process", END)
graph = builder.compile()

result = graph.invoke({"input": "hello", "result": ""})
```

### Conditional Routing
```python
def router(state):
    return "path_a" if state["score"] > 5 else "path_b"

builder.add_conditional_edges("check_node", router, {"path_a": "node_a", "path_b": "node_b"})
```

### Loop (Retry Until Done)
```python
builder.add_conditional_edges("check", router, {"retry": "generate", "done": "final"})
builder.add_edge("generate", "check")  # feedback back to check
```

### Memory (MemorySaver)
```python
from langgraph.checkpoint.memory import MemorySaver
graph = builder.compile(checkpointer=MemorySaver())
graph.invoke(state, config={"configurable": {"thread_id": "user_1"}})
```

### Parallel Execution
```python
from typing import Annotated
from operator import add

class State(TypedDict):
    results: Annotated[list, add]

builder.add_edge("start", "task_a")
builder.add_edge("start", "task_b")   # both run in parallel
builder.add_edge("task_a", "merge")
builder.add_edge("task_b", "merge")
```

### ReAct Tools Agent
```python
from langchain_core.tools import tool

@tool
def my_tool(input: str) -> str:
    """Description of what this tool does."""
    return "result"

llm_with_tools = llm.bind_tools([my_tool])
```

---

## 📚 Read the `notes.md` in Each Folder!

Every day folder has a `notes.md` with:
- ✅ What the concept is
- ✅ Why you use it
- ✅ Real-life use cases
- ✅ Code examples from your actual files
- ✅ Comparison tables (vs LangChain)
- ✅ Important keywords glossary
- ✅ Beginner-friendly analogies

---

## 🔄 LangGraph vs LangChain — Full Comparison

| Feature | LangChain | LangGraph |
|---------|-----------|-----------|
| Flow model | Linear chain | Graph (any shape) |
| Loops | ❌ | ✅ Native cycles |
| Conditional routing | Limited | ✅ Conditional edges |
| State management | Memory objects | ✅ Typed shared state |
| Human-in-the-loop | Manual | ✅ interrupt_before/after |
| Parallel execution | asyncio only | ✅ Fan-out/Fan-in |
| Multi-agent | Manual orchestration | ✅ Supervisor pattern |
| Streaming | chain.stream() | ✅ graph.stream() |
| Checkpointing | ❌ | ✅ MemorySaver, SqliteSaver |

---

*Happy learning! You've covered a full professional LangGraph curriculum. 🎓*
