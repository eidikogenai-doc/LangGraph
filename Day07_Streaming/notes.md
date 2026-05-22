# Day 7 — Streaming

## What is the concept?
**Streaming** means seeing output **as it's being generated** — word by word (LLM streaming) or step by step (graph streaming) — instead of waiting for the complete response.

---

## Why do we use it?
- Better user experience — responses appear instantly
- Long outputs feel faster even though total time is the same
- Graph streaming lets you monitor which node is running in real time
- Critical for production chatbots and long-running agent workflows

---

## Two Types of Streaming in LangGraph

### Type 1: LLM Token Streaming
Stream the LLM's response word by word as it generates:

```python
llm = ChatGroq(model="llama-3.1-8b-instant", streaming=True)

for chunk in llm.stream("Explain quantum computing"):
    print(chunk.content, end="", flush=True)
```

### Type 2: Graph Node Streaming
Stream graph execution — see each node's output as it completes:

```python
for step in graph.stream({"input": "your question"}):
    print("Node completed:", step)
```

---

## Combined: Both at Once
Inside a graph node, use `llm.stream()` AND use `graph.stream()` to run it:

```python
def explain_node(state):
    full_text = ""
    for chunk in llm.stream(f"Explain: {state['input']}"):
        print(chunk.content, end="", flush=True)   # live token output
        full_text += chunk.content
    state["result"] = full_text
    return state

# Run the graph with streaming (see each node complete)
for step in graph.stream({"input": user_input}):
    print("\\n📌 Node done:", list(step.keys()))
```

---

## `flush=True` — Why It Matters
`print(chunk, end="", flush=True)` — the `flush=True` forces Python to immediately write each chunk to the terminal. Without it, Python buffers output and you'd see nothing until the full response is done.

---

## Streaming Modes (LangGraph graph.stream)

| Mode | What you see |
|------|-------------|
| `graph.stream(state)` | Dict of `{node_name: node_output}` after each node |
| `graph.astream(state)` | Async version — for async applications |
| `graph.stream_events(state)` | Detailed events: node_start, node_end, llm_token |

---

## Real-Life Use Cases
| Scenario | Stream Type |
|----------|------------|
| Chatbot typing effect | LLM token streaming |
| Monitoring a long pipeline | Graph node streaming |
| Dashboard showing agent progress | Graph node streaming |
| Large document summarizer | Both combined |

---

## Important Keywords
| Term | Meaning |
|------|---------|
| `streaming=True` | Enable token streaming on the LLM |
| `llm.stream(prompt)` | Returns an iterator of text chunks |
| `graph.stream(state)` | Returns an iterator of node outputs |
| `chunk.content` | The text content of one streaming token |
| `end=""` | Prevent newline between chunks |
| `flush=True` | Force immediate terminal output |

---

## Beginner-Friendly Analogy
Streaming is like **watching a chef cook vs receiving a finished meal**:
- **No streaming** = kitchen is closed, you wait 20 mins, meal arrives complete
- **LLM streaming** = you can see the chef adding ingredients in real-time
- **Graph streaming** = you see each station (prep → grill → plate) complete live 🍳
