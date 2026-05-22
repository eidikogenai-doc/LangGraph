# Day 5 — Memory & Checkpointing

## What is the concept?
**Memory** in LangGraph means persisting conversation history or state **across invocations** so the agent remembers what was said before. **Checkpointing** is LangGraph's built-in mechanism to save and restore graph state at any point.

---

## Why do we use it?
- Without memory, every `graph.invoke()` is completely isolated — the agent forgets everything
- With memory, you can build chatbots that remember users, context, and prior decisions
- Checkpointing also enables **resuming** a long workflow after an interruption
- It enables **Human-in-the-Loop** (pause → human reviews → resume)

---

## Two Approaches

### Approach 1: Manual JSON Memory (Simple)
Save conversation history to a JSON file yourself:
```python
history = load_from_json("memory.json")
history.append({"role": "user", "content": user_input})
response = llm.invoke(history)
history.append({"role": "assistant", "content": response.content})
save_to_json(history)
```
✅ Simple, no LangGraph dependency
❌ Not integrated with graph state

### Approach 2: LangGraph MemorySaver (Built-in)
Use LangGraph's official checkpointer:
```python
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()
graph = builder.compile(checkpointer=checkpointer)

# Run with a thread_id to maintain separate memory per user
config = {"configurable": {"thread_id": "user_123"}}
graph.invoke({"messages": [...]}, config=config)
```
✅ Native integration with graph state
✅ Multiple threads = multiple users
✅ Can resume mid-graph

---

## Part 1: Thread-based Memory

Each conversation is a **thread**. Different thread IDs = completely separate memory:

```
thread_id="alice" → Alice's conversation history
thread_id="bob"   → Bob's conversation history  (isolated)
```

---

## Part 2: Message History in State

Store messages as a list in state:
```python
from typing import Annotated
from operator import add
from langchain_core.messages import HumanMessage, AIMessage

class ChatState(TypedDict):
    messages: Annotated[list, add]   # ← list accumulates via add operator
```

The `Annotated[list, add]` tells LangGraph: "when merging state, add new messages to the existing list" rather than replacing it.

---

## Comparison: Memory Approaches
| Approach | Persistence | Multi-user | Resume graph |
|----------|------------|-----------|--------------|
| Manual JSON | ✅ File-based | Manual | ❌ |
| MemorySaver | ✅ In-memory | ✅ thread_id | ✅ |
| SqliteSaver | ✅ SQLite DB | ✅ thread_id | ✅ |

---

## Important Keywords
| Term | Meaning |
|------|---------|
| `MemorySaver` | Built-in in-memory checkpointer |
| `thread_id` | Unique ID that identifies a conversation session |
| `config` | Dict passed to `invoke()` with thread_id |
| `Annotated[list, add]` | State field that accumulates (appends) new values |
| Checkpoint | A snapshot of graph state at a given step |
| `get_state(config)` | Inspect the saved state of a thread |

---

## Beginner-Friendly Analogy
Memory in LangGraph is like a **notebook for each customer**:
- `MemorySaver` = the filing cabinet
- `thread_id` = the customer's name on the folder
- Each `invoke()` = reading and adding to that customer's notebook
- Different thread IDs = different customer notebooks (fully isolated)
