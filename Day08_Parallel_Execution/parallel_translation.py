import os
from typing import TypedDict, Annotated
from operator import add
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
class TranslationState(TypedDict):
    text: str
    translations: Annotated[list, add]

# ─────────────────────────────────────────────
# 🔹 Parallel Translation Nodes
# ─────────────────────────────────────────────

def translate_hindi(state: TranslationState) -> dict:
    res = llm.invoke(f"Translate to Hindi (Devanagari script): {state['text']}")
    return {"translations": [f"🇮🇳 Hindi:  {res.content.strip()}"]}

def translate_spanish(state: TranslationState) -> dict:
    res = llm.invoke(f"Translate to Spanish: {state['text']}")
    return {"translations": [f"🇪🇸 Spanish: {res.content.strip()}"]}

def translate_french(state: TranslationState) -> dict:
    res = llm.invoke(f"Translate to French: {state['text']}")
    return {"translations": [f"🇫🇷 French:  {res.content.strip()}"]}

def translate_japanese(state: TranslationState) -> dict:
    res = llm.invoke(f"Translate to Japanese: {state['text']}")
    return {"translations": [f"🇯🇵 Japanese: {res.content.strip()}"]}

def merge_translations(state: TranslationState) -> TranslationState:
    print("\n✅ All translations complete.")
    return state

# ─────────────────────────────────────────────
# 🔧 Build Graph
# ─────────────────────────────────────────────
builder = StateGraph(TranslationState)

builder.add_node("start",    lambda x: x)
builder.add_node("hindi",    translate_hindi)
builder.add_node("spanish",  translate_spanish)
builder.add_node("french",   translate_french)
builder.add_node("japanese", translate_japanese)
builder.add_node("merge",    merge_translations)

builder.set_entry_point("start")

# Fan-out
for lang in ["hindi", "spanish", "french", "japanese"]:
    builder.add_edge("start", lang)
    builder.add_edge(lang, "merge")

builder.add_edge("merge", END)

graph = builder.compile()

# ─────────────────────────────────────────────
# 🚀 Run
# ─────────────────────────────────────────────
text = input("Enter text to translate (English): ")
print("\n🌍 Translating into 4 languages in parallel...\n")

result = graph.invoke({"text": text, "translations": []})

print("\n" + "="*55)
print(f"🌐 Translations for: \"{text}\"")
print("="*55)
for t in result["translations"]:
    print(f"  {t}")
