# Day 2 — StateGraph & Nodes

## What is the concept?
The **StateGraph** is the core building block of LangGraph. You define a **typed state** (using Python's `TypedDict`), add **nodes** (functions), connect them with **edges**, and compile into a runnable graph.

---

## Why do we use it?
- `TypedDict` gives you **type safety** — you know exactly what keys live in state
- Nodes are **pure functions** — easy to test and reason about
- The graph structure makes your AI workflow **explicit and visual**
- Compiling validates your graph before running it

---

## Part 1: TypedDict State

### What it is
A typed dictionary that defines all the fields your graph's shared state will have.

### Why not just use a plain dict?
Plain dicts are fine for simple graphs, but `TypedDict` gives you:
- IDE autocomplete on state keys
- Validation that you're not misspelling keys
- Clear documentation of what flows through the graph

### Code
```python
from typing import TypedDict

class MyState(TypedDict):
    question: str
    answer: str
    is_done: bool
```

---

## Part 2: Nodes

### What a Node is
A regular Python function with this signature:
```python
def my_node(state: MyState) -> MyState:
    # do something with state
    state["answer"] = "Hello"
    return state
```

### Rules for Nodes
1. Always accepts `state` as first argument
2. Always returns the modified state (or a partial dict in newer LangGraph)
3. Can call LLMs, APIs, databases — anything

---

## Part 3: Edges

### Direct Edge
Runs next node unconditionally:
```python
builder.add_edge("node_a", "node_b")
```

### Entry Point
Sets which node runs first:
```python
builder.set_entry_point("node_a")
```

### Ending the Graph
Connect to END to stop the graph:
```python
from langgraph.graph import END
builder.add_edge("last_node", END)
```

---

## Part 4: Sequential Graph (A → B → C)

```
[input_node] → [process_node] → [output_node] → END
```

This is the simplest graph — identical to a LangChain chain but with explicit state.

---

## Comparison: LangChain Chain vs LangGraph Sequential
| Feature | LangChain Chain | LangGraph Sequential |
|---------|----------------|---------------------|
| Syntax | `a \| b \| c` | `add_edge(a, b)` |
| State | Implicit dict | Explicit TypedDict |
| Inspect mid-run | Hard | Easy (stream) |
| Add branches later | Requires rewrite | Just add conditional edge |
| Loops | Not supported | Add cycle anytime |

---

## Important Keywords
| Term | Meaning |
|------|---------|
| `TypedDict` | Python typing class for typed dictionaries |
| `StateGraph(State)` | Graph that carries your State type |
| `add_node(name, fn)` | Register a function as a node |
| `add_edge(a, b)` | Connect node a → node b |
| `set_entry_point(name)` | Set the first node to run |
| `compile()` | Validate and build the runnable graph |
| `invoke(state)` | Run the graph with an initial state |
| `END` | Special constant that marks graph exit |

---

## Beginner-Friendly Analogy
StateGraph is like a **relay race**:
- **State** = the baton (passed between runners)
- **Nodes** = the runners (each does their part)
- **Edges** = the track (determines who passes to whom)
- `compile()` = the race official checks everyone is ready
- `invoke()` = fire the starting gun 🏁
