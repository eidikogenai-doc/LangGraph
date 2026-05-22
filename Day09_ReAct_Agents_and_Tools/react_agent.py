import os
import ast
import operator
import datetime
import requests
from typing import TypedDict, Annotated
from operator import add
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, SystemMessage

load_dotenv()

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY")
)

# ─────────────────────────────────────────────
# 🔧 Tools
# ─────────────────────────────────────────────

@tool
def calculator(expression: str) -> str:
    """Use this when the user asks to calculate or solve a math problem.
    Input must be a valid math expression like '25 * 4' or '100 / 5 + 3'."""
    allowed_ops = {
        ast.Add: operator.add, ast.Sub: operator.sub,
        ast.Mult: operator.mul, ast.Div: operator.truediv,
        ast.Pow: operator.pow, ast.Mod: operator.mod,
    }
    def _eval(node):
        if isinstance(node, ast.Constant):
            return node.n
        elif isinstance(node, ast.BinOp):
            op_fn = allowed_ops.get(type(node.op))
            if op_fn is None:
                raise ValueError("Unsupported operator")
            return op_fn(_eval(node.left), _eval(node.right))
        elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            return -_eval(node.operand)
        raise ValueError("Invalid expression")
    try:
        result = _eval(ast.parse(expression, mode="eval").body)
        return f"Result: {result}"
    except Exception as e:
        return f"Math Error: {e}"


@tool
def get_current_date(dummy: str = "") -> str:
    """Use this when the user asks for today's date or current time."""
    now = datetime.datetime.now()
    return f"Today is {now.strftime('%A, %B %d, %Y')} and the time is {now.strftime('%I:%M %p')}."


@tool
def weather(city: str) -> str:
    """Use this when the user asks for the current weather in a city."""
    api_key = os.getenv("WEATHER_API_KEY", "")
    if not api_key:
        return f"Weather API key not set. (Simulated) Weather in {city}: 28°C, partly cloudy."
    try:
        response = requests.get(
            f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={city}",
            timeout=10
        )
        data = response.json()
        if "error" in data:
            return f"Weather Error: {data['error']['message']}"
        c = data["current"]
        return (
            f"🌤 Weather in {city}: {c['temp_c']}°C / {c['temp_f']}°F, "
            f"{c['condition']['text']}, Humidity: {c['humidity']}%, "
            f"Wind: {c['wind_kph']} kph"
        )
    except Exception as e:
        return f"Weather Error: {e}"


tools = [calculator, get_current_date, weather]
tools_by_name = {t.name: t for t in tools}
llm_with_tools = llm.bind_tools(tools)

# ─────────────────────────────────────────────
# 🧠 State — messages accumulate
# ─────────────────────────────────────────────
class AgentState(TypedDict):
    messages: Annotated[list, add]

# ─────────────────────────────────────────────
# 🔹 Nodes
# ─────────────────────────────────────────────

SYSTEM = SystemMessage(content=(
    "You are a helpful AI assistant with access to tools: calculator, weather, and date. "
    "Use tools only when needed. Give direct, concise answers."
))

def agent_node(state: AgentState) -> dict:
    """LLM reasons and decides: answer directly OR call a tool"""
    messages = [SYSTEM] + state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

def tool_node(state: AgentState) -> dict:
    """Execute all tool calls requested by the LLM"""
    last_message = state["messages"][-1]
    tool_results = []

    for tool_call in last_message.tool_calls:
        tool_fn = tools_by_name.get(tool_call["name"])
        if tool_fn:
            result = tool_fn.invoke(tool_call["args"])
            print(f"  🔧 {tool_call['name']}({tool_call['args']}) → {result}")
        else:
            result = f"Tool '{tool_call['name']}' not found."

        tool_results.append(
            ToolMessage(content=result, tool_call_id=tool_call["id"])
        )

    return {"messages": tool_results}

# ─────────────────────────────────────────────
# 🔀 Router — should we call tools or are we done?
# ─────────────────────────────────────────────
def should_use_tools(state: AgentState) -> str:
    last = state["messages"][-1]
    if isinstance(last, AIMessage) and last.tool_calls:
        return "call_tools"
    return "done"

# ─────────────────────────────────────────────
# 🔧 Build ReAct Graph
# ─────────────────────────────────────────────
builder = StateGraph(AgentState)

builder.add_node("agent", agent_node)
builder.add_node("tools", tool_node)

builder.set_entry_point("agent")

# Agent decides: call tools OR done
builder.add_conditional_edges(
    "agent",
    should_use_tools,
    {
        "call_tools": "tools",   # → execute tools
        "done":        END       # → return answer
    }
)

# After tools, go back to agent (ReAct loop)
builder.add_edge("tools", "agent")

graph = builder.compile()

# ─────────────────────────────────────────────
# 🚀 Run
# ─────────────────────────────────────────────
print("🤖 ReAct Agent with Tools (type 'bye' to exit)")
print("Tools available: calculator, weather, date\n")

while True:
    user_input = input("You: ").strip()
    if not user_input:
        continue
    if user_input.lower() == "bye":
        print("👋 Goodbye!")
        break

    result = graph.invoke({"messages": [HumanMessage(content=user_input)]})

    # Find last AIMessage with text content
    for msg in reversed(result["messages"]):
        if isinstance(msg, AIMessage) and msg.content:
            print(f"\n🤖 AI: {msg.content}\n")
            break
