
# """
# inference.py — AI Incident Response Environment
# Baseline inference script for the OpenEnv RL Hackathon.

# Output format:
#   [START] task=<task_name> env=<benchmark> model=<model_name>
#   [STEP]  step=<n> action=<action_str> reward=<0.00> done=<true|false> error=<msg|null>
#   [END]   success=<true|false> steps=<n> rewards=<r1,r2,...,rn>
# """

# import os
# import sys
# import json

# # ─── Environment variables ─────────────────────────────────────────────────
# API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
# MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
# HF_TOKEN = os.getenv("HF_TOKEN")

# if HF_TOKEN is None:
#     raise ValueError("HF_TOKEN environment variable is required")

# # ─── OpenAI client ─────────────────────────────────────────────────────────
# from openai import OpenAI

# client = OpenAI(
#     base_url=API_BASE_URL,
#     api_key=HF_TOKEN,
# )

# # ─── Environment ───────────────────────────────────────────────────────────
# from env.environment import IncidentResponseEnv, Action
# from env.tasks import TASKS, PRIMARY_TASKS

# ENV_NAME = "incident-response-env"


# def build_system_prompt() -> str:
#     return (
#         "You are an expert cybersecurity and legal analyst specializing in incident response. "
#         "You will be given a real-world incident scenario and must respond precisely as instructed. "
#         "Follow the instructions exactly — do not add explanations unless asked. "
#         "Be concise, accurate, and structured."
#     )


# class APIFatalError(Exception):
#     """Raised on errors that should abort the episode (quota, auth, etc.)."""
#     pass


# def call_llm(system: str, user: str) -> str:
#     """Call the LLM and return the response content. Raises APIFatalError on quota/auth issues."""
#     try:
#         response = client.chat.completions.create(
#             model=MODEL_NAME,
#             messages=[
#                 {"role": "system", "content": system},
#                 {"role": "user", "content": user},
#             ],
#             max_tokens=1024,
#             temperature=0.0,
#         )
#         return response.choices[0].message.content or ""
#     except Exception as e:
#         err_str = str(e)
#         # Fatal errors — no point retrying
#         if any(code in err_str for code in ["429", "401", "403", "quota", "billing", "Unauthorized"]):
#             raise APIFatalError(err_str)
#         return f"ERROR:{err_str}"


# def run_episode(task_id: str) -> dict:
#     """Run a single episode for a given task. Returns result dict."""
#     env = IncidentResponseEnv(task_id=task_id)
#     obs = env.reset()

#     task_name = obs.task_name
#     rewards = []
#     steps_done = 0
#     success = False
#     final_error = None

#     print(f"[START] task={task_name} env={ENV_NAME} model={MODEL_NAME}")

#     system_prompt = build_system_prompt()

#     try:
#         for step_num in range(1, obs.max_steps + 1):
#             # Build user prompt from current observation
#             user_prompt = (
#                 f"=== INCIDENT REPORT ===\n{obs.incident_description}\n\n"
#                 f"=== INSTRUCTIONS ===\n{obs.instructions}"
#             )

#             # Get LLM response — abort immediately on fatal API errors
#             try:
#                 action_content = call_llm(system_prompt, user_prompt)
#             except APIFatalError as e:
#                 final_error = str(e)
#                 err_short = str(e)[:80]
#                 print(
#                     f"[STEP] step={step_num} action='API_ERROR' "
#                     f"reward=0.00 done=true error={err_short}"
#                 )
#                 break

#             # Step the environment
#             action = Action(content=action_content)
#             obs, reward, done, info = env.step(action)

#             rewards.append(reward)
#             steps_done = step_num
#             last_error = info.get("last_action_error")
#             if last_error:
#                 final_error = last_error

#             # Sanitize action string for output (single line, no newlines)
#             action_str = str(action_content).replace("\n", " ").replace("\r", "")[:120]
#             error_str = str(last_error) if last_error else "null"
#             done_str = "true" if done else "false"

#             print(
#                 f"[STEP] step={step_num} action={action_str!r} "
#                 f"reward={reward:.2f} done={done_str} error={error_str}"
#             )

#             if done:
#                 success = reward >= 0.6
#                 break

#     except Exception as e:
#         final_error = str(e)
#         # Ensure [END] is always printed
#     finally:
#         env.close()

#     rewards_str = ",".join(f"{r:.2f}" for r in rewards)
#     success_str = "true" if success else "false"
#     print(
#         f"[END] success={success_str} steps={steps_done} rewards={rewards_str}"
#     )

#     return {
#         "task_id": task_id,
#         "task_name": task_name,
#         "success": success,
#         "steps": steps_done,
#         "rewards": rewards,
#         "final_error": final_error,
#     }


# def main():
#     """Run all tasks and print summary."""
#     results = []

#     for task in PRIMARY_TASKS:
#         print(f"\n{'='*60}")
#         print(f"Running task: {task.task_id} [{task.difficulty}]")
#         print("=" * 60)
#         result = run_episode(task.task_id)
#         results.append(result)

#     # Summary
#     print("\n" + "=" * 60)
#     print("BASELINE SUMMARY")
#     print("=" * 60)
#     for r in results:
#         avg_reward = sum(r["rewards"]) / len(r["rewards"]) if r["rewards"] else 0.0
#         print(
#             f"  {r['task_name']:30s}  success={str(r['success']):5s}  "
#             f"steps={r['steps']}  avg_reward={avg_reward:.2f}"
#         )

#     total_success = sum(1 for r in results if r["success"])
#     print(f"\nTotal tasks passed: {total_success}/{len(results)}")


# if __name__ == "__main__":
#     main()
# 
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn



from env.environment import IncidentResponseEnv, Action

# Initialize environment globally
env = IncidentResponseEnv()

def reset():
    obs = env.reset()
    
    return {
        "observation": str(obs.incident_description),
        "info": str(obs.instructions)
    }

def step(action: str):
    action_obj = Action(content=action)
    obs, reward, done, info = env.step(action_obj)

    return {
        "observation": str(obs.incident_description),
        "reward": float(reward),
        "done": bool(done),
        "info": str(info)
    }
    

app = FastAPI()

class ActionInput(BaseModel):
    action: str

@app.post("/reset")
def api_reset():
    return reset()

@app.post("/step")
def api_step(input: ActionInput):
    return step(input.action)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)