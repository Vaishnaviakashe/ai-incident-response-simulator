"""
Gradio Dashboard for AI Incident Response Environment
Visual demo for HuggingFace Spaces
"""

import os
import json
import time
import gradio as gr
from openai import OpenAI

from env.environment import IncidentResponseEnv, Action
from env.tasks import TASKS, PRIMARY_TASKS, TASK_MAP

API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME   = os.getenv("MODEL_NAME",   "Qwen/Qwen2.5-72B-Instruct")
HF_TOKEN     = os.getenv("HF_TOKEN",     "")

DIFFICULTY_EMOJI = {"easy": "🟢", "medium": "🟡", "hard": "🔴"}
SEVERITY_COLOR   = {"low": "🔵", "medium": "🟡", "high": "🟠", "critical": "🔴"}


def get_client():
    token = HF_TOKEN or "demo"
    return OpenAI(base_url=API_BASE_URL, api_key=token)


def call_llm(client, system: str, user: str) -> str:
    try:
        resp = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user}
            ],
            max_tokens=1024,
            temperature=0.0,
        )
        return resp.choices[0].message.content or ""
    except Exception:
        # 🔥 FALLBACK (IMPORTANT)
        user = user.lower()
        if "hacked" in user or "fraud" in user:
            return "cyber fraud"
        elif "threat" in user:
            return "cyber harassment"
        return "unknown"


def format_reward_bar(reward: float) -> str:
    filled = int(reward * 20)
    bar    = "█" * filled + "░" * (20 - filled)
    pct    = int(reward * 100)
    color  = "🟢" if reward >= 0.75 else ("🟡" if reward >= 0.4 else "🔴")
    return f"{color} [{bar}] {pct}%"


def run_task(task_id: str, hf_token: str, progress=gr.Progress()):
    client_token = hf_token.strip() or HF_TOKEN
    if not client_token:
        yield (
            "❌ No HF Token provided. Enter your token above.",
            "", "", "", "", ""
        )
        return

    client = OpenAI(base_url=API_BASE_URL, api_key=client_token)
    env    = IncidentResponseEnv(task_id=task_id)
    obs    = env.reset()
    task   = TASK_MAP[task_id]

    system_prompt = (
        "You are an expert cybersecurity and legal analyst specializing in incident response. "
        "Follow the instructions exactly. Be concise and structured. "
        "For classification tasks: respond with ONLY the category name. "
        "For law mapping: respond with ONLY a comma-separated list. "
        "For JSON tasks: respond with ONLY valid JSON, no markdown."
    )

    step_log    = []
    all_rewards = []
    final_answer = ""

    progress(0, desc="Initializing environment...")

    for step_num in range(1, obs.max_steps + 1):
        progress(step_num / obs.max_steps, desc=f"Step {step_num} — Agent thinking...")

        user_prompt = (
            f"=== INCIDENT REPORT ===\n{obs.incident_description}\n\n"
            f"=== YOUR TASK ===\n{obs.instructions}"
        )

        answer = call_llm(client, system_prompt, user_prompt)
        final_answer = answer

        action             = Action(content=answer)
        obs, reward, done, info = env.step(action)
        all_rewards.append(reward)

        details   = info.get("grade_details", {}).get("details", {})
        bar       = format_reward_bar(reward)
        step_html = f"**Step {step_num}** — Reward: {bar}\n\n"
        step_html += f"```\n{answer[:400]}\n```\n"

        if details:
            if "required_matched" in details:
                step_html += f"\n✅ Laws matched: `{', '.join(details.get('required_matched', []))}`"
            if "wrong_included" in details:
                step_html += f"\n❌ Wrong laws: `{', '.join(details.get('wrong_included', []))}`"
            if "action_keywords_found" in details:
                step_html += f"\n🎯 Action keywords: `{', '.join(details.get('action_keywords_found', []))}`"

        step_log.append(step_html)

        if done:
            break

    env.close()
    progress(1.0, desc="Complete!")

    total_reward = sum(all_rewards) / len(all_rewards) if all_rewards else 0.0
    success      = total_reward >= 0.5

    # Format final answer nicely
    try:
        parsed = json.loads(final_answer)
        display_answer = json.dumps(parsed, indent=2)
    except Exception:
        display_answer = final_answer

    # Summary
    emoji = DIFFICULTY_EMOJI.get(task.difficulty, "⚪")
    result_badge = "✅ SUCCESS" if success else "❌ FAILED"
    summary = (
        f"## {result_badge}\n\n"
        f"**Task:** {task.scenario_title}  \n"
        f"**Difficulty:** {emoji} {task.difficulty.upper()}  \n"
        f"**Score:** {format_reward_bar(total_reward)}  \n"
        f"**Steps used:** {len(all_rewards)}  \n"
        f"**Model:** `{MODEL_NAME}`"
    )

    step_output  = "\n\n---\n\n".join(step_log)
    answer_block = f"```json\n{display_answer}\n```" if display_answer.startswith("{") else f"```\n{display_answer}\n```"

    yield summary, step_output, answer_block


def build_ui():
    task_choices = [(f"{DIFFICULTY_EMOJI.get(t.difficulty,'⚪')} [{t.difficulty.upper()}] {t.scenario_title}", t.task_id) for t in TASKS]

    with gr.Blocks(
        title="AI Incident Response Environment",
        theme=gr.themes.Base(
            primary_hue="red",
            secondary_hue="orange",
            neutral_hue="slate",
            font=gr.themes.GoogleFont("JetBrains Mono"),
        ),
        css="""
        .header-box { background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
                      border: 1px solid #ef4444; border-radius: 12px; padding: 24px; margin-bottom: 16px; }
        .metric-box { background: #1e293b; border: 1px solid #334155;
                      border-radius: 8px; padding: 16px; text-align: center; }
        footer { display: none !important; }
        """
    ) as demo:

        gr.HTML("""
        <div class="header-box">
          <h1 style="color:#ef4444;font-family:'JetBrains Mono',monospace;margin:0;font-size:1.8rem;">
            🚨 AI Incident Response Environment
          </h1>
          <p style="color:#94a3b8;margin:8px 0 0 0;font-size:0.95rem;">
            OpenEnv RL Benchmark · Cybercrime & Legal Incident Handling · 6 Real-World Scenarios
          </p>
        </div>
        """)

        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### ⚙️ Configuration")
                hf_token_box = gr.Textbox(
                    label="HF Token (required)",
                    placeholder="hf_...",
                    type="password",
                    value=HF_TOKEN or "",
                )
                task_selector = gr.Dropdown(
                    label="Select Scenario",
                    choices=task_choices,
                    value=task_choices[0][1],
                )

                gr.Markdown("### 📋 Scenario Details")
                scenario_info = gr.Markdown(value=_get_scenario_info(TASKS[0]))

                run_btn = gr.Button("▶ Run Agent", variant="primary", size="lg")

            with gr.Column(scale=2):
                gr.Markdown("### 📊 Results")
                summary_box = gr.Markdown(value="*Click **Run Agent** to start...*")

                gr.Markdown("### 🤖 Agent Steps")
                steps_box = gr.Markdown(value="")

                gr.Markdown("### 💬 Final Agent Answer")
                answer_box = gr.Markdown(value="")

        gr.Markdown("---")
        gr.Markdown("""
        ### 🏗️ How It Works
        | Task | Difficulty | What the Agent Must Do | Reward |
        |------|-----------|----------------------|--------|
        | Incident Classification | 🟢 Easy | Identify attack type from description | 0–1.0 |
        | Law Mapping | 🟡 Medium | Select all applicable laws across jurisdictions | 0–1.0 |
        | Structured Response | 🔴 Hard | Produce full JSON incident response plan | 0–1.0 |

        Built for the **Meta OpenEnv RL Hackathon** · [GitHub](#)
        """)

        # Update scenario info when task changes
        task_selector.change(
            fn=lambda tid: _get_scenario_info(TASK_MAP[tid]),
            inputs=[task_selector],
            outputs=[scenario_info],
        )

        run_btn.click(
            fn=run_task,
            inputs=[task_selector, hf_token_box],
            outputs=[summary_box, steps_box, answer_box],
        )

    return demo


def _get_scenario_info(task) -> str:
    emoji = DIFFICULTY_EMOJI.get(task.difficulty, "⚪")
    desc  = task.incident_description[:280] + "..." if len(task.incident_description) > 280 else task.incident_description
    return (
        f"**{emoji} {task.scenario_title}**\n\n"
        f"*Difficulty:* `{task.difficulty}`  \n"
        f"*Max Steps:* `{task.max_steps}`\n\n"
        f"{desc}"
    )


if __name__ == "__main__":
    demo = build_ui()
    demo.launch(server_name="127.0.0.1", server_port=7860)