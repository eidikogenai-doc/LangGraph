# Day 3 — Conditional Edges (Routing / Branching)

## What is the concept?
**Conditional edges** let your graph take different paths based on the current state. Instead of always going A → B, the graph can decide: "if this condition, go to B; otherwise go to C."

---

## Why do we use it?
- Build **smart routers** that send users to different departments
- Create **decision gates** — skip steps if not needed
- Implement **retry logic** — go back if quality isn't good enough
- Enable **multi-path workflows** — different actions for different inputs

---

## How It Works

### 1. Write a router function
Takes state, returns a **string key** (not state):

```python
def router(state):
    if state["sentiment"] == "positive":
        return "celebrate"
    elif state["sentiment"] == "negative":
        return "apologize"
    else:
        return "neutral"
```

### 2. Register it as conditional edges
```python
builder.add_conditional_edges(
    "sentiment_node",     # source node
    router,               # router function
    {
        "celebrate": "celebrate_node",   # key → target node
        "apologize": "apologize_node",
        "neutral":   "neutral_node"
    }
)
```

---

## Visual Flow
```
                    [router node]
                         ↓
           ┌─────────────┼─────────────┐
           ↓             ↓             ↓
    [celebrate]     [apologize]    [neutral]
           ↓             ↓             ↓
          END           END           END
```

---

## Part 1: Simple Sentiment Router

Classify user input as positive / negative / neutral and respond differently.

```python
def classify(state):
    response = llm.invoke(f"Classify sentiment as 'positive', 'negative', or 'neutral': {state['text']}")
    state["sentiment"] = response.content.strip().lower()
    return state

def route_sentiment(state):
    if "positive" in state["sentiment"]:
        return "positive"
    elif "negative" in state["sentiment"]:
        return "negative"
    return "neutral"
```

---

## Part 2: Intent Router

Route based on what the user wants to do (question / task / smalltalk).

---

## Comparison Table
| Type | Use When |
|------|----------|
| Direct edge `add_edge` | Always go from A → B |
| Conditional edge | Different paths based on state |
| Loop (conditional back) | Retry or iterate until condition met |

---

## Important Keywords
| Term | Meaning |
|------|---------|
| `add_conditional_edges(src, fn, map)` | Add smart routing from a node |
| Router function | Returns a string key, not state |
| Path map | Dict mapping string keys to node names |
| `END` | Terminal node — graph stops here |

---

## Beginner-Friendly Analogy
Conditional edges are like a **GPS navigation decision**:
- You reach a fork in the road (a node)
- GPS checks current conditions (router function)
- Routes you to the best path (conditional edge map)
- Each path leads to a different destination (nodes)
