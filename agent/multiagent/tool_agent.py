from tool_intelligence.router import intelligent_tool_call


class ToolAgent:

    async def execute(self, step):

        result = await intelligent_tool_call(step["input"])

        return {
            "step": step["step"],
            "output": result["output"]
        }