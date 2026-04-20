from mem0 import Memory

config = {
    "vector_store": {
        "provider": "chroma",
        "config": {
            "collection_name": "whatsapp_agent",
            "path": "./chroma_db",
        }
    },
    "llm": {
        "provider": "groq",
        "config": {
            "model": "llama-3.3-70b-versatile"
        }
    },
    "embedder": {
        "provider": "ollama",
        "config": {
            "model": "nomic-embed-text",
            "ollama_base_url": "http://localhost:11434"
        }
    }
}

memory = Memory.from_config(config)


def add_memory(user_text, assistant_text):
    memory.add(
        messages=[
            {"role": "user", "content": user_text},
            {"role": "assistant", "content": assistant_text}
        ],
        user_id="me"
    )


def search_memory(query):
    return memory.search(query, filters={"user_id": "me"}, limit=5)