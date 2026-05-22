# Day 6 — Human-in-the-Loop

## What is the concept?
**Human-in-the-Loop (HITL)** means pausing the graph at a specific step to wait for a human to review, approve, edit, or reject the AI's output — before the graph continues.

---

## Why do we use it?
- AI makes mistakes — humans catch them before they cause problems
- High-stakes decisions (sending emails, making purchases) need approval
- Regulated industries (healthcare, finance) require human sign-off
- Allows users to **guide** the AI mid-workflow, not just at the start

---

## How It Works in LangGraph

### Pattern: interrupt + resume
1. Graph runs to the review node
2. Human reads the output, gives input (approve / edit / reject)
3. Graph continues based on human decision

```python
def human_review(state):
    print("AI output:", state["draft"])
    approval = input("Approve? (yes/no): ")
    if approval == "no":
        feedback = input("Feedback: ")
        state["feedback"] = feedback
    state["approved"] = approval
    return state

def decision(state):
    return "final" if state["approved"] == "yes" else "improve"
```

---

## Visual Flow (Email Approval Example)
```
[generate_draft]
        ↓
[human_review]  ← ⏸️  PAUSES for human input
        ↓
   approved?
   yes ↓    no ↓
[final]   [improve]
               ↓
          [human_review]  ← 🔁 loop back
```

---

## Real-Life Use Cases
| Use Case | Human Reviews |
|----------|--------------|
| Email drafter | Approve / edit before sending |
| Code generator | Review before deployment |
| Medical report | Doctor signs off before filing |
| Social media post | PR team approves before posting |
| Financial report | Manager approves before submitting |

---

## Three HITL Patterns

### Pattern 1: Approve / Reject
Binary decision — human either approves or sends back for improvement.

### Pattern 2: Edit in Place
Human edits the content directly — their edited version becomes the new state.

### Pattern 3: Multi-stage Approval
Multiple reviewers in sequence — each must approve before the next step.

---

## Important Keywords
| Term | Meaning |
|------|---------|
| HITL | Human-in-the-Loop — human inserted into AI workflow |
| Approval node | A graph node that waits for human input |
| Feedback loop | Human gives notes → AI improves → human re-reviews |
| `interrupt_before` | LangGraph feature to pause before a specific node |
| `interrupt_after` | LangGraph feature to pause after a specific node |

---

## Beginner-Friendly Analogy
HITL is like **a chef presenting a dish to the head chef** before it goes to the customer:
- AI sous chef prepares the dish (generate node)
- Head chef tastes it (human review node)
- "Needs more salt" → back to kitchen (improvement loop)
- "Perfect" → serve it (final node) 🍽️
