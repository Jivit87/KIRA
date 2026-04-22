import asyncio

from multiagent.planner_agent import PlannerAgent
from multiagent.tool_agent import ToolAgent
from multiagent.memory_agent import MemoryAgent
from multiagent.research_agent import ResearchAgent


class Coordinator:

    def __init__(self):
        self.planner = PlannerAgent()
        self.tools = ToolAgent()
        self.memory = MemoryAgent()
        self.research = ResearchAgent()


    async def run_step(self, step):

        if step["agent"] == "research":
            return await self.research.execute(step)

        elif step["agent"] == "tools":
            return await self.tools.execute(step)

        else:
            return {
                "step": step["step"],
                "output": "Unknown agent"
            }


    async def handle(self, message):

        # get memory
        context = await self.memory.retrieve(
            message
        )

        # build plan
        plan = await self.planner.create_plan(
            message,
            context
        )

        steps = plan["steps"]

        results = []

        i = 0

        while i < len(steps):

            current = steps[i]

            group = current.get(
                "parallel_group"
            )


            # ------------------------
            # PARALLEL EXECUTION BLOCK
            # ------------------------

            if group:

                grouped_tasks = []

                print(f"[PARALLEL GROUP] {group}")

                while (
                    i < len(steps)
                    and steps[i].get("parallel_group") == group
                ):

                    grouped_tasks.append(
                        self.run_step(
                            steps[i]
                        )
                    )

                    i += 1


                # run all simultaneously
                parallel_results = await asyncio.gather(
                    *grouped_tasks,
                    return_exceptions=True
                )


                for r in parallel_results:

                    if isinstance(
                        r,
                        Exception
                    ):
                        results.append({
                            "error": str(r)
                        })

                    else:
                        results.append(r)


            # ------------------------
            # NORMAL STEP
            # ------------------------

            else:
                r = await self.run_step(current)
                results.append(r)

                i += 1


        # summarize results
        summary = await self.planner.summarize(results)

        await self.memory.store(message,summary)

        return summary