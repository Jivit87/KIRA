import os
from groq import Groq
from streaming import stream_status
from tool_intelligence.router import intelligent_tool_call
from utils.risk_detector import is_risky
from confirmation import request_confirmation
from planner.state import save_plan_state

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))


async def execute_plan(plan: dict, sender: str, start_index: int = 0, context: dict = None):
    """
    Execute a plan step by step.

    plan:        the plan dict from create_plan() with a "steps" list
    sender:      WhatsApp JID — used to send status messages and save state
    start_index: which step to start from (used when resuming a paused plan)
    context:     results from already-completed steps (passed forward)
    """
    steps = plan.get("steps", [])
    context = context or {}  # stores output from each step, passed to next steps

    for i, step in enumerate(steps):
        # Skip steps we already completed (when resuming)
        if i < start_index:
            continue

        step_num   = step.get("step", i + 1)
        tool       = step.get("tool", "")
        params     = step.get("params", {})
        desc       = step.get("description", "")
        is_critical = step.get("critical", False)

        # Show the user what we're doing right now
        await stream_status(f"⏳ Step {step_num}: {desc}")

        # ── ask_user ──────────────────────────────────────────────────────────
        # Pause the plan and wait for the user to reply before continuing
        if tool == "ask_user":
            question = params.get("question", desc)
            await stream_status(f"❓ {question}\n\nReply to continue.")
            # Save state so we can resume from the NEXT step after user replies
            save_plan_state(sender, plan, i + 1, context)
            return  # stop here — orchestrator will resume on next message

        # ── llm_reply ─────────────────────────────────────────────────────────
        # Generate a text summary using the LLM — no tool call
        if tool == "llm_reply":
            prompt = params.get("prompt", desc)
            # Include context from previous steps in the summary
            context_summary = "\n".join(
                f"Step {k}: {v}" for k, v in context.items()
            )
            full_prompt = f"{prompt}\n\nCompleted steps:\n{context_summary}" if context_summary else prompt

            try:
                response = groq_client.chat.completions.create(
                    model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
                    messages=[
                        {"role": "system", "content": "Summarize the completed task results for the user. Be concise. Plain text only."},
                        {"role": "user",   "content": full_prompt}
                    ]
                )
                reply = response.choices[0].message.content
            except Exception as e:
                reply = f"✅ Steps completed. (Summary failed: {e})"

            await stream_status(reply)
            context[f"step_{step_num}"] = reply
            continue

        # ── regular tool ──────────────────────────────────────────────────────
        # Check if this tool + params is risky before running
        risky, reason = is_risky(tool, params)

        if risky:
            # Ask for confirmation — pause the plan
            await request_confirmation(sender, tool, params, reason)
            # Save state so we can resume from THIS step after YES
            save_plan_state(sender, plan, i, context)
            return  # stop here — orchestrator resumes after YES/NO

        # Run the tool through the intelligence layer (retry + fallback)
        result = await intelligent_tool_call(tool, params)

        if result["error"]:
            await stream_status(f"⚠️ Step {step_num} failed: {result['error']}")

            if is_critical:
                await stream_status("❌ Critical step failed. Aborting plan.")
                return
            else:
                await stream_status("⏭ Skipping and continuing...")
                continue

        # Step succeeded — save output to context for future steps
        output = result["output"]
        context[f"step_{step_num}"] = output

    await stream_status("✅ Plan complete.")
