from tools.research import web_search 

class ResearchAgent:

    async def excute(self, step):

        query = step["input"]

        results = web_search(query)

        return {
            "step": step["step"],
            "output": results
        }