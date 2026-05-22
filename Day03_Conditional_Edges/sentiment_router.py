import os
from typing import TypedDict
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq

load_dotenv()

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY")
)

# ─────────────────────────────────────────────
# 🧠 State
# ─────────────────────────────────────────────
class SentimentState(TypedDict):
    text: str
    sentiment: str
    response: str

# ─────────────────────────────────────────────
# 🔹 Nodes
# ─────────────────────────────────────────────

def classify_sentiment(state: SentimentState) -> SentimentState:
    """Classify the sentiment of user text"""
    response = llm.invoke(
        f"Classify the sentiment of this text as exactly one word: 'positive', 'negative', or 'neutral'.\n"
        f"Text: {state['text']}\nReply with only one word."
    )
    state["sentiment"] = response.content.strip().lower()
    print(f"🔍 Detected sentiment: {state['sentiment']}")
    return state

def positive_response(state: SentimentState) -> SentimentState:
    """Respond to positive sentiment"""
    response = llm.invoke(f"The user said something positive: '{state['text']}'. Respond with enthusiasm and encouragement in 1-2 sentences.")
    state["response"] = f"😊 {response.content}"
    return state

def negative_response(state: SentimentState) -> SentimentState:
    """Respond to negative sentiment"""
    response = llm.invoke(f"The user said something negative: '{state['text']}'. Respond with empathy and helpful advice in 1-2 sentences.")
    state["response"] = f"💙 {response.content}"
    return state

def neutral_response(state: SentimentState) -> SentimentState:
    """Respond to neutral sentiment"""
    response = llm.invoke(f"The user said: '{state['text']}'. Give a balanced, informative response in 1-2 sentences.")
    state["response"] = f"💬 {response.content}"
    return state

# ─────────────────────────────────────────────
# 🔀 Router function — returns string key
# ─────────────────────────────────────────────
def route_by_sentiment(state: SentimentState) -> str:
    if "positive" in state["sentiment"]:
        return "positive"
    elif "negative" in state["sentiment"]:
        return "negative"
    return "neutral"

# ─────────────────────────────────────────────
# 🔧 Build Graph
# ─────────────────────────────────────────────
builder = StateGraph(SentimentState)

builder.add_node("classify", classify_sentiment)
builder.add_node("positive_node", positive_response)
builder.add_node("negative_node", negative_response)
builder.add_node("neutral_node", neutral_response)

builder.set_entry_point("classify")

# 🔥 Conditional routing after classify
builder.add_conditional_edges(
    "classify",
    route_by_sentiment,
    {
        "positive": "positive_node",
        "negative": "negative_node",
        "neutral":  "neutral_node"
    }
)

builder.add_edge("positive_node", END)
builder.add_edge("negative_node", END)
builder.add_edge("neutral_node", END)

graph = builder.compile()

# ─────────────────────────────────────────────
# 🚀 Run
# ─────────────────────────────────────────────
print("🤖 Sentiment-Aware Chatbot (type 'bye' to exit)\n")

while True:
    text = input("You: ")
    if text.lower() == "bye":
        print("Goodbye 👋")
        break

    result = graph.invoke({"text": text, "sentiment": "", "response": ""})
    print(f"AI: {result['response']}\n")
