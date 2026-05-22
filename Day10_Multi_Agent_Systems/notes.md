# Day 10 — Multi-Agent Systems

## What is the concept?
A **multi-agent system** consists of multiple specialized AI agents working together — each expert in one area — coordinated by a **supervisor agent** that decides which agent to call and when.

---

## Why do we use it?
- Complex tasks benefit from **specialization** — one agent per domain
- Agents can be developed and tested independently
- The supervisor decides the workflow dynamically at runtime
- Scales to arbitrarily complex workflows without one monolithic prompt

---

## Architecture: Supervisor + Subagents

### Supervisor Agent
- Receives user request
- Decides which subagent to call next
- Collects results
- Knows when the task is complete

### Subagents
- Each is a specialist (researcher, writer, coder, analyst)
- Has its own system prompt and possibly its own tools
- Reports back to supervisor with results

### Visual Flow
```
[User Request]
       ↓
[Supervisor]  ← decides routing
       ↓
  ┌────┴────┐
  ↓         ↓
[Researcher] [Writer]   ← specialized subagents
  ↓         ↓
[Supervisor]  ← collects results, decides next step
       ↓
[Final Answer]
```

---

## Implementation Pattern

### Subagent as a function
```python
def researcher_agent(state):
    response = llm.invoke(
        [SystemMessage("You are a research expert. Find key facts.")]
        + state["messages"]
    )
    return {"messages": [AIMessage(content=f"[RESEARCHER]: {response.content}")]}
```

### Supervisor with dynamic routing
```python
def supervisor(state):
    response = llm.invoke(
        [SystemMessage("You are a supervisor. Decide: researcher, writer, or FINISH.")]
        + state["messages"]
    )
    # Parse the routing decision from the response
    if "FINISH" in response.content:
        state["next"] = "FINISH"
    elif "researcher" in response.content.lower():
        state["next"] = "researcher"
    else:
        state["next"] = "writer"
    return state

def route_supervisor(state):
    return state["next"]
```

---

## Real-Life Use Cases
| System | Agents |
|--------|--------|
| Content creation | Researcher + Writer + Editor + SEO Checker |
| Software development | Planner + Coder + Tester + Documenter |
| Customer service | Classifier + FAQ Agent + Escalation Agent |
| Financial analysis | Data Agent + Analyst + Risk Assessor + Reporter |
| Travel planning | Hotel Agent + Flight Agent + Activity Agent + Budget Agent |

---

## Comparison: Single Agent vs Multi-Agent
| Aspect | Single Agent | Multi-Agent |
|--------|-------------|-------------|
| Complexity | One big prompt | Specialized prompts |
| Maintainability | Harder | Easier (isolate bugs) |
| Performance | One LLM call | Multiple focused calls |
| Scalability | Limited | Add agents as needed |
| Best for | Simple tasks | Complex multi-step tasks |

---

## Important Keywords
| Term | Meaning |
|------|---------|
| Supervisor agent | Orchestrator that routes to subagents |
| Subagent | Specialist agent for one domain |
| Routing decision | Supervisor decides which agent runs next |
| `FINISH` | Special signal that the task is complete |
| Handoff | Passing control from supervisor to a subagent |
| Orchestration | Coordinating multiple agents toward a goal |

---

## Beginner-Friendly Analogy
Multi-agent systems are like a **well-managed company**:
- **Supervisor** = CEO or manager (delegates, decides)
- **Researcher agent** = research department (finds facts)
- **Writer agent** = marketing department (creates content)
- **Coder agent** = engineering team (builds features)
- Each department is expert in its lane, and the CEO decides who works when 🏢
