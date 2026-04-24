from tool_intelligence.router import intelligent_tool_call


class ToolAgent:

    async def execute(self, step: dict) -> dict:
        """Run a tool call for the given step."""
        tool_name = step.get("tool", "")
        params    = step.get("params", {})

        # If no structured params, fall back to passing input as text
        if not params and step.get("input"):
            params = {"input": step["input"]}

        result = await intelligent_tool_call(tool_name, params)
        return {
            "step":   step["step"],
            "output": result.get("output") or result.get("error", "No output")
        }
