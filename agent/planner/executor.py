from tools.router import run_action
from streaming import stream_status

async def execute_plan(plan, sender):
    steps = plan.get("steps", [])

    for step in steps:
        step_num = step.get("step")
        action = step.get("action", "")
        tool = step.get("tool", "")
        input_data = step.get("input", "")

        await stream_status(f"⏳ Step {step_num}: {action}", sender)

        if tool == "reply":
            await stream_status(input_data, sender)

        elif tool == "ask_user":
            await stream_status(f"❓ {input_data}", sender)
            return  # stop until user replies

        else:
            result = run_action(input_data)
            await stream_status(f"✅ {result}", sender)

    await stream_status("🎉 Plan completed", sender)