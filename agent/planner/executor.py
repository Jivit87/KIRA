from tools.router import run_action
from streaming import stream_status
from tool_intelligence.router import intelligent_tool_call

FALLBACKS = {
    "open vscode": "open code",
    "open chrome": "open safari"
}


async def execute_plan(plan, sender):
    steps = plan.get("steps", [])
    context = {}

    for step in steps:
        step_num = step.get("step")
        if not step_num:
            continue

        action = step.get("action", "")
        tool = step.get("tool", "")
        input_data = step.get("input", "")

        # Debug (important for dev)
        print(f"[Tool] {tool} → {input_data}")

        # Step status
        await stream_status(f"⏳ Step {step_num}: {action}", sender)

        # Direct reply
        if tool == "reply":
            await stream_status(input_data, sender)
            continue

        # Ask user (pause execution)
        elif tool == "ask_user":
            await stream_status(f"❓ {input_data}\n(Reply to continue)", sender)
            return  # future: resume from here

        # Tool execution
        else:
            # Pass context (basic memory)
            enriched_input = f"{input_data} | context: {context}"

            result = await intelligent_tool_call(enriched_input)

            # Handle failure
            if result.get("error"):
                fallback = None

                # smarter fallback match
                for key in FALLBACKS:
                    if key in input_data.lower():
                        fallback = FALLBACKS[key]
                        break

                if fallback:
                    await stream_status(f"🔄 Trying fallback: {fallback}", sender)
                    result = await intelligent_tool_call(fallback)

                # still failed
                if result.get("error"):
                    await stream_status(f"❌ Failed: {result['error']}", sender)
                    await stream_status("⚠️ Skipping step due to failure", sender)
                    continue

            # Success
            output = result.get("output", "No output")
            await stream_status(f"✅ {output}", sender)

            # Save context
            context[f"step_{step_num}"] = output

    await stream_status("🎉 Plan completed", sender)