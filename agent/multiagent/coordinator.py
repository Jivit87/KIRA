import asyncio
from multiagent.planner_agent  import PlannerAgent
from multiagent.tool_agent     import ToolAgent
from multiagent.memory_agent   import MemoryAgent
from multiagent.research_agent import ResearchAgent


class Coordinator:
    """
    Orchestrates multiple specialized agents to handle a user message.
    - PlannerAgent  : breaks the goal into steps
    - ResearchAgent : handles web search steps
    - ToolAgent     : handles Mac tool steps
    - MemoryAgent   : retrieves and stores long-term memory
    """

    def __init__(self):
        self.planner  = PlannerAgent()
        self.tools    = ToolAgent()
        self.memory   = MemoryAgent()
        self.research = ResearchAgent()

    async def run_step(self, step: dict) -> dict:
        """Route a single step to the right agent."""
        agent = step.get("agent", "tools")

        if agent == "research":
            return await self.research.execute(step)
        else:
            return await self.tools.execute(step)

    async def handle(self, message: str) -> str:
        """
        Full pipeline:
          1. Retrieve memory context
          2. Create a plan
          3. Execute steps (parallel if same parallel_group, sequential otherwise)
          4. Summarize results
          5. Store to memory
        """
        # 1. Get relevant memory
        context = await self.memory.retrieve(message)

        # 2. Build a plan
        plan  = await self.planner.create_plan(message, context)
        steps = plan.get("steps", [])

        results = []
        i = 0

        while i < len(steps):
            current = steps[i]
            group   = current.get("parallel_group")

            if group:
                # Collect all steps in the same parallel group
                grouped = []
                while i < len(steps) and steps[i].get("parallel_group") == group:
                    grouped.append(self.run_step(steps[i]))
                    i += 1

                # Run them all at the same time
                parallel_results = await asyncio.gather(*grouped, return_exceptions=True)

                for r in parallel_results:
                    if isinstance(r, Exception):
                        results.append({"error": str(r)})
                    else:
                        results.append(r)
            else:
                # Run this step normally
                r = await self.run_step(current)
                results.append(r)
                i += 1

        # 3. Summarize all results into one reply
        summary = await self.planner.summarize(results)

        # 4. Save to memory
        await self.memory.store(message, summary)

        return summary
