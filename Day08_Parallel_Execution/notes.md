# Day 8 — Parallel Execution (Fan-out / Fan-in)

## What is the concept?
**Parallel execution** means running multiple graph nodes **at the same time** — instead of one after another. LangGraph supports this natively through **fan-out** (one node → many nodes) and **fan-in** (many nodes → one merge node).

---

## Why do we use it?
- **Speed**: 3 tasks in parallel takes the same time as 1 task instead of 3x
- **Independence**: tasks that don't depend on each other can run simultaneously
- **Richer output**: combine multiple AI perspectives in one response

---

## Fan-out / Fan-in Pattern

### Fan-out: One → Many
```python
builder.add_edge("start", "task_a")   # start → task_a
builder.add_edge("start", "task_b")   # start → task_b (same time!)
builder.add_edge("start", "task_c")   # start → task_c (same time!)
```

### Fan-in: Many → One (merge)
```python
builder.add_edge("task_a", "merge")   # all converge...
builder.add_edge("task_b", "merge")
builder.add_edge("task_c", "merge")   # ...into merge node
```

### Visual Flow
```
           [start]
          ↙   ↓   ↘
      [a]    [b]    [c]    ← run in parallel
          ↘   ↓   ↙
           [merge]         ← combine results
              ↓
            [END]
```

---

## The `Annotated[list, add]` Pattern

When multiple nodes write to the same state key, you need a **reducer** to tell LangGraph how to combine them:

```python
from typing import Annotated
from operator import add

class ParallelState(TypedDict):
    input: str
    results: Annotated[list, add]   # ← add = list concatenation
```

- `add` = append new list items to existing list
- Without this, parallel nodes would overwrite each other's output!

---

## Real-Life Use Cases
| Use Case | Parallel Tasks |
|----------|---------------|
| Document analysis | Summarize + Classify + Extract keywords simultaneously |
| Travel planner | Research hotels + flights + activities at once |
| Code review | Check style + bugs + performance simultaneously |
| Market research | Analyze competitor A + B + C in parallel |
| Language processing | Translate to French + Spanish + Hindi at once |

---

## Comparison: Sequential vs Parallel
| Approach | 3 LLM calls | Total time |
|----------|------------|-----------|
| Sequential | One after another | ~3 × latency |
| Parallel (fan-out) | All at once | ~1 × latency |

---

## Important Keywords
| Term | Meaning |
|------|---------|
| Fan-out | One node connecting to multiple nodes |
| Fan-in | Multiple nodes connecting to one merge node |
| Reducer | Function that combines parallel state updates (e.g. `add`) |
| `Annotated[list, add]` | State field that accumulates results from parallel nodes |
| `operator.add` | Combines lists by appending: `[a] + [b] = [a, b]` |

---

## Beginner-Friendly Analogy
Parallel execution is like a **restaurant kitchen with specialized stations**:
- Head chef gets the order (start node)
- Simultaneously: grill station, sauce station, and garnish station all work (parallel nodes)
- All plates combined for final presentation (merge node) 🍽️
