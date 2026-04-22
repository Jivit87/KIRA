from memory.mem0_client import add_memory, search_memory


class MemoryAgent:

    async def retrieve(self, query):

        return search_memory(query)


    async def store(self, user_text, summary):

        add_memory(
            user_text,
            summary
        )