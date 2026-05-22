import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

# ─────────────────────────────────────────────
# 🔥 streaming=True — enables token-by-token output
# ─────────────────────────────────────────────
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY"),
    streaming=True
)

print("🤖 LLM Token Streaming Demo (type 'bye' to exit)\n")

while True:
    user_input = input("You: ").strip()

    if user_input.lower() == "bye":
        print("AI: Goodbye! 👋")
        break

    print("AI: ", end="", flush=True)

    # 🔥 Stream token by token
    for chunk in llm.stream(user_input):
        print(chunk.content, end="", flush=True)

    print("\n")  # newline after full response
