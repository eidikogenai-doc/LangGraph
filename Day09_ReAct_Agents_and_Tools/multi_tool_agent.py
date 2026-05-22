import os
import ast
import datetime
import operator
import random
import requests
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, ToolMessage

load_dotenv()

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY")
)

# ─────────────────────────────────────────────
# 🔧 Define Tools
# ─────────────────────────────────────────────

@tool
def calculator(expression: str) -> str:
    """Useful for performing mathematical calculations. Input must be a valid math expression."""
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
        raise ValueError("Unsupported expression")
    try:
        return f"Result: {_eval(ast.parse(expression, mode='eval').body)}"
    except Exception as e:
        return f"Math Error: {e}"


@tool
def weather(city: str) -> str:
    """Useful for getting current weather of any city."""
    api_key = os.getenv("WEATHER_API_KEY", "")
    if not api_key:
        return f"(Simulated) Weather in {city}: 30°C, sunny. Set WEATHER_API_KEY for real data."
    try:
        response = requests.get(
            f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={city}",
            timeout=10
        )
        data = response.json()["current"]
        return (
            f"🌤 Weather in {city}: {data['temp_c']}°C, "
            f"{data['condition']['text']}, Humidity: {data['humidity']}%"
        )
    except Exception as e:
        return f"Weather Error: {e}"


@tool
def current_date(dummy: str = "") -> str:
    """Useful for getting today's current date."""
    return f"📅 Today is {datetime.datetime.now().strftime('%A, %d %B %Y')}"


@tool
def motivation(dummy: str = "") -> str:
    """Useful for getting a motivational quote or inspiration."""
    quotes = [
        "Success comes from consistency 🔥",
        "Discipline beats motivation 💪",
        "Never stop learning 🚀",
        "Your future is shaped by what you do today 📈",
        "Every expert was once a beginner 🌱",
    ]
    return random.choice(quotes)


# ─────────────────────────────────────────────
# 🔗 Bind tools to LLM
# ─────────────────────────────────────────────
tools = [calculator, weather, current_date, motivation]
tools_by_name = {t.name: t for t in tools}
llm_with_tools = llm.bind_tools(tools)

# ─────────────────────────────────────────────
# 🚀 Multi-turn Agent Loop
# ─────────────────────────────────────────────
print("🤖 Multi-Tool Agent (type 'bye' to exit)")
print(f"Available tools: {', '.join(tools_by_name.keys())}\n")

while True:
    user_input = input("You: ").strip()
    if not user_input:
        continue
    if user_input.lower() == "bye":
        print("👋 Goodbye!")
        break

    messages = [HumanMessage(content=user_input)]
    response = llm_with_tools.invoke(messages)
    messages.append(response)

    # If LLM wants to call tools
    if response.tool_calls:
        for tc in response.tool_calls:
            tool_fn = tools_by_name.get(tc["name"])
            if tool_fn:
                result = tool_fn.invoke(tc["args"])
                print(f"  🔧 {tc['name']} → {result}")
            else:
                result = f"Tool '{tc['name']}' not found."
            messages.append(ToolMessage(content=result, tool_call_id=tc["id"]))

        # Final response after tool results
        final = llm_with_tools.invoke(messages)
        print(f"\n🤖 AI: {final.content}\n")
    else:
        print(f"\n🤖 AI: {response.content}\n")
