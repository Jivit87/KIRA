from tools.research import web_search


class ResearchAgent:

    async def execute(self, step: dict) -> dict:
        """Run a web search for the given step's input."""
        query = step.get("input", "")
        result = web_search(query)
        return {
            "step":   step["step"],
            "output": result
        }
