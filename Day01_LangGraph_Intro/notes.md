# Day 1 — Introduction to LangGraph

## What is the concept?
LangGraph is an open-source Python framework built **on top of LangChain** that lets you build stateful, multi-step AI workflows as **graphs** — where nodes are processing steps and edges control the flow between them.

## Why do we use it?
LangChain chains are linear (A → B → C). LangGraph adds:
- **Loops** — retry until satisfied
- **Conditional branching** — different paths based on AI output
- **State persistence** — remember data across nodes
- **Human-in-the-loop** — pause and wait for human approval
- **Parallel execution** — run multiple nodes at the same time

## Small Explanation
LangGraph models your AI workflow as a **directed graph**:
- **Nodes** — functions that process or transform state
- **Edges** — connections that define what runs next
- **State** — a shared dictionary passed through every node
- **Conditional Edges** — smart routing based on state values
- **Checkpointing** — save and restore state mid-graph

## Real-Life Use Cases
- Email drafting agent that loops until human approves
- Customer service bot that routes to different departments
- Code review agent that retries until tests pass
- Research agent that searches, summarizes, and validates
- Multi-step document processor with parallel analysis

## Important Keywords
| Term | Meaning |
|------|---------|
| `StateGraph` | The main graph class you build your workflow with |
| `Node` | A function that receives state, modifies it, returns state |
| `Edge` | A direct connection from one node to another |
| `Conditional Edge` | A smart connection that routes based on state |
| `State` | A shared TypedDict (or dict) passed through all nodes |
| `Entry Point` | The first node the graph runs |
| `END` | Special constant marking the graph's exit |
| `Checkpointer` | Saves state so you can resume or inspect mid-run |
| `compile()` | Locks the graph and returns a runnable object |

## Your Setup
```python
# Install LangGraph
# pip install langgraph langchain-groq python-dotenv

from langgraph.graph import StateGraph
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY")
)

# Simple test
response = llm.invoke("What is LangGraph?")
print(response.content)
```

## LangGraph Core Architecture (Big Picture)
```
Your Input
     ↓
[Entry Node]       ← first function to run
     ↓
[Node 2]           ← processes / transforms state
     ↓  (or conditional branch)
[Node 3]           ← more processing
     ↓
[END]              ← graph finishes, returns final state
```

## LangGraph vs LangChain — Key Differences
| Feature | LangChain | LangGraph |
|---------|-----------|-----------|
| Flow type | Linear (A→B→C) | Graph (any shape) |
| Loops | ❌ Not native | ✅ Built-in cycles |
| Conditional routing | Limited | ✅ Conditional edges |
| State management | Memory objects | ✅ Typed shared state |
| Human-in-the-loop | Manual | ✅ Native interrupt |
| Parallel execution | asyncio only | ✅ Fan-out/Fan-in |

## Learning Progression in Your Project
```
Day 1  → LangGraph basics + setup + why it exists
Day 2  → StateGraph, Nodes, TypedDict State
Day 3  → Conditional Edges (branching / routing)
Day 4  → Loops and Cycles (retry, feedback loops)
Day 5  → Memory and Checkpointing (persistent state)
Day 6  → Human-in-the-Loop (approval workflows)
Day 7  → Streaming (real-time node + LLM output)
Day 8  → Parallel Execution (fan-out / fan-in)
Day 9  → ReAct Agents with Tools inside graphs
Day 10 → Multi-Agent Systems (supervisor + subagents)
```

## Beginner-Friendly Explanation
Think of LangGraph like a **flowchart that thinks**:
- **Nodes** = boxes on the flowchart (do the work)
- **Edges** = arrows between boxes (define order)
- **Conditional Edges** = diamond decision points
- **State** = the sticky note passed between boxes
- **Loop** = an arrow pointing backwards to retry

You draw the flowchart once, compile it, and LangGraph runs it. 🗺️
