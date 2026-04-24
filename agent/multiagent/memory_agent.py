from memory.mem0_client import add_memory, search_memory


class MemoryAgent:

    async def retrieve(self, query: str) -> list:
        """Search long-term memory for context relevant to the query."""
        return search_memory(query)

    async def store(self, user_text: str, summary: str):
        """Save a completed task exchange to long-term memory."""
        add_memory(user_text, summary)
