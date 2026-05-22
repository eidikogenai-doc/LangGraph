# Day 9 — ReAct Agents & Tools in LangGraph

## What is the concept?
A **ReAct Agent** is an AI that can use **tools** (functions) to answer questions. ReAct stands for **Reason + Act** — the AI reasons about what to do, acts by calling a tool, observes the result, and repeats until it has a final answer.

LangGraph lets you build ReAct agents as proper graphs where each reasoning step is a node.

---

## Why do we use it?
- LLMs alone can't access real-time data, do math, or query databases
- Tools extend the LLM's abilities with real capabilities
- Graph structure makes the agent's reasoning steps **visible and debuggable**
- You control exactly when and how tools are called

---

## How ReAct Works

### The ReAct Loop
```
[User Input]
     ↓
[LLM Reasons] → "I need to check the weather. I'll call the weather tool."
     ↓
[Tool Call: weather("London")]
     ↓
[Tool Result: "Rainy, 15°C"]
     ↓
[LLM Reasons] → "I have the data. I can answer now."
     ↓
[Final Answer]
```

### In LangGraph
```
[agent node]  ← LLM decides: answer directly OR call a tool
     ↓
conditional edge: "tool_call" or "done"
     ↓
[tool node]   ← executes the actual tool
     ↓
[agent node]  ← back to LLM with tool result (loop!)
```

---

## Defining Tools with `@tool`

```python
from langchain_core.tools import tool

@tool
def get_weather(city: str) -> str:
    """Get the current weather for a city."""
    # call weather API...
    return f"Sunny, 25°C in {city}"
```

Rules:
- Use `@tool` decorator
- Write a clear docstring — the LLM uses it to decide WHEN to call the tool
- Type-annotate parameters
- Always return a string

---

## Binding Tools to LLM

```python
tools = [calculator, weather, motivation]
llm_with_tools = llm.bind_tools(tools)
```

After binding, the LLM can return `tool_calls` in its response instead of a text answer.

---

## Tool Types You Can Build
| Tool Type | Example |
|-----------|---------|
| API tool | Weather, stock prices, news |
| Calculator | Math expression evaluator |
| Database | SQL query runner |
| Search | Web search |
| File | Read/write files |
| System | Run shell commands |
| Custom | Any Python function |

---

## Important Keywords
| Term | Meaning |
|------|---------|
| `@tool` | Decorator that turns a function into a LangChain tool |
| `bind_tools(tools)` | Attach tools to an LLM |
| `tool_calls` | List of tools the LLM wants to call |
| `ToolMessage` | Message type carrying a tool's result |
| `HumanMessage` | User's input message |
| `AIMessage` | LLM's response (may include tool_calls) |
| ReAct | Reason + Act loop for tool-using agents |

---

## Beginner-Friendly Analogy
A ReAct agent is like a **smart assistant with a toolbox**:
- You ask: "What's the weather in Mumbai?"
- Assistant thinks: "I need the weather tool for this" (Reason)
- Assistant opens the weather tool and checks (Act)
- Reads the result: "32°C, sunny" (Observe)
- Answers you: "It's 32°C and sunny in Mumbai" (Answer) ☀️
