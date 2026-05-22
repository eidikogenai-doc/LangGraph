# Day 4 — Loops & Cycles

## What is the concept?
**Loops** in LangGraph let you run nodes repeatedly until a condition is satisfied. Instead of a one-pass pipeline, you create a **cycle** — an edge that points back to a previous node.

---

## Why do we use it?
- **Quality validation**: retry until output meets a standard
- **User confirmation**: keep asking until user says yes
- **Feedback loops**: refine a document based on critique
- **Retry on error**: re-run a tool if it fails
- **Iterative refinement**: improve output across multiple passes

---

## How It Works

### Creating a Loop
A loop is just a conditional edge that points **backwards**:

```python
builder.add_conditional_edges(
    "check_quality",      # node that decides
    quality_router,       # router function
    {
        "pass": "final",  # exit loop ✅
        "fail": "improve" # loop back 🔁
    }
)
builder.add_edge("improve", "check_quality")  # back to checker
```

### Visual Flow
```
[generate] → [check_quality]
                    ↓           ↓
               "pass"       "fail"
                    ↓           ↓
               [final]    [improve] ─┐
                                      └──→ [check_quality]  (loop!)
```

---

## Important: Preventing Infinite Loops
Always include a **counter** in your state:

```python
class LoopState(TypedDict):
    content: str
    attempts: int      # ← track iteration count
    max_attempts: int  # ← set a hard limit
```

And check it in your router:
```python
def router(state):
    if state["quality"] == "good" or state["attempts"] >= state["max_attempts"]:
        return "end"
    return "retry"
```

---

## Real-Life Use Cases
| Use Case | Loop Logic |
|----------|-----------|
| Essay writer | Loop until quality score > 8/10 |
| Password validator | Loop until valid password entered |
| Code generator | Loop until code passes tests |
| Translation checker | Loop until back-translation matches |
| Email drafter | Loop until user approves |

---

## Comparison
| Feature | No Loop | With Loop |
|---------|---------|-----------|
| Passes through nodes | Once | Multiple times |
| Good for | Static pipelines | Iterative refinement |
| Risk | None | Infinite loop (guard with counter) |

---

## Important Keywords
| Term | Meaning |
|------|---------|
| Cycle | An edge that creates a loop in the graph |
| `attempts` | Counter to prevent infinite loops |
| `max_attempts` | Hard limit on iterations |
| Back-edge | An edge pointing to an earlier node |
| Convergence | When the loop's exit condition is met |

---

## Beginner-Friendly Analogy
A loop is like **editing a document with a strict professor**:
- You write a draft (generate node)
- Professor grades it (check node)
- Grade < 7? Rewrite (loop back to generate)
- Grade ≥ 7? Submit (exit to final node) ✅
