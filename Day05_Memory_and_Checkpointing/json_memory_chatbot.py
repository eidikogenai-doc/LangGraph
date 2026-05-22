import os
import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY")
)

MEMORY_FILE = "conversation_memory.json"

# ─────────────────────────────────────────────
# 🧠 JSON Memory Functions
# ─────────────────────────────────────────────

def load_memory(session_id: str) -> list:
    """Load conversation history for a session from file"""
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            all_sessions = json.load(f)
            return all_sessions.get(session_id, [])
    return []

def save_memory(session_id: str, history: list):
    """Save conversation history to file"""
    all_sessions = {}
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            all_sessions = json.load(f)
    all_sessions[session_id] = history
    with open(MEMORY_FILE, "w") as f:
        json.dump(all_sessions, f, indent=2)

def clear_memory(session_id: str):
    """Clear memory for a session"""
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            all_sessions = json.load(f)
        all_sessions.pop(session_id, None)
        with open(MEMORY_FILE, "w") as f:
            json.dump(all_sessions, f, indent=2)
    print(f"🗑️  Memory cleared for session '{session_id}'")

# ─────────────────────────────────────────────
# 🚀 Persistent Chat with JSON Checkpointing
# ─────────────────────────────────────────────
print("🤖 AI with Persistent JSON Memory")
print("Commands: 'bye' = exit | 'clear' = clear memory | 'history' = show history\n")

session_id = input("Session ID: ").strip() or "default"
history = load_memory(session_id)

system_message = {
    "role": "system",
    "content": "You remember everything the user has told you. Reference past context naturally."
}

if history:
    print(f"📂 Loaded {len(history)} messages from previous session.\n")
else:
    print(f"🆕 New session started: '{session_id}'\n")

while True:
    user_input = input("You: ").strip()

    if user_input.lower() == "bye":
        save_memory(session_id, history)
        print(f"AI: Goodbye! Saved {len(history)} messages. 👋")
        break

    elif user_input.lower() == "clear":
        history = []
        clear_memory(session_id)
        continue

    elif user_input.lower() == "history":
        print(f"\n📜 History ({len(history)} messages):")
        for msg in history[-6:]:  # show last 6
            role = "You" if msg["role"] == "user" else "AI"
            print(f"  {role}: {msg['content'][:80]}...")
        print()
        continue

    # Append user message
    history.append({"role": "user", "content": user_input})

    # Call LLM with full history
    response = llm.invoke([system_message] + history)
    ai_reply = response.content

    print(f"AI: {ai_reply}\n")

    # Append AI reply and save checkpoint
    history.append({"role": "assistant", "content": ai_reply})
    save_memory(session_id, history)
