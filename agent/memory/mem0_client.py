import os
from mem0 import Memory

config = {
    "vector_store": {
        "provider": "chroma",
        "config": {
            "collection_name": "whatsapp_agent",
            "path": os.getenv("CHROMA_PATH", "./chroma_db"),
        }
    },
    "llm": {
        "provider": "groq",
        "config": {
            "model": os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        }
    },
    "embedder": {
        "provider": "ollama",
        "config": {
            "model": "nomic-embed-text",
            "ollama_base_url": os.getenv("OLLAMA_URL", "http://localhost:11434")
        }
    }
}

# Single shared memory instance — reused across all calls
memory = Memory.from_config(config)


def add_memory(user_text: str, assistant_text: str):
    """
    Save a conversation exchange to long-term memory.
    Mem0 automatically decides what's worth keeping.
    """
    memory.add(
        messages=[
            {"role": "user",      "content": user_text},
            {"role": "assistant", "content": assistant_text}
        ],
        user_id="me"
    )


def search_memory(query: str, limit: int = 5) -> list:
    """
    Search past memory for context relevant to the current message.
    Returns a list of dicts like: [{"memory": "user likes dark themes", ...}]
    """
    results = memory.search(query, user_id="me", limit=limit)

    # mem0 can return either a list or a dict with a "results" key
    if isinstance(results, dict):
        return results.get("results", [])
    return results if isinstance(results, list) else []
