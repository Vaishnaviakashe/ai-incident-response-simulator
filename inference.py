# import os
# from fastapi import FastAPI, Request
# from pydantic import BaseModel
# from env.environment import IncidentResponseEnv, Action

# app = FastAPI()
# env = IncidentResponseEnv()
# HF_TOKEN = os.getenv("HF_TOKEN")

# class ActionInput(BaseModel):
#     action: str

# @app.get("/")
# async def root():
#     return {"status": "alive", "message": "OpenEnv API"}

# @app.post("/reset")
# async def api_reset():
#     obs = env.reset()
#     # CRITICAL: Print [START] so the validator knows the task began
#     print(f"[START] task={getattr(env, 'task_id', 'incident_task')}", flush=True)
#     return {
#         "observation": str(obs.incident_description),
#         "info": str(obs.instructions)
#     }

# @app.post("/step")
# async def api_step(input: ActionInput):
#     action_obj = Action(content=input.action)
#     obs, reward, done, info = env.step(action_obj)
    
#     # CRITICAL: Print [STEP] for every action taken
#     step_num = info.get("step_count", 1) 
#     print(f"[STEP] step={step_num} reward={reward}", flush=True)
    
#     if done:
#         # CRITICAL: Print [END] when the task is finished
#         total_reward = info.get("total_reward", reward)
#         print(f"[END] task={getattr(env, 'task_id', 'incident_task')} score={total_reward} steps={step_num}", flush=True)
        
#     return {
#         "observation": str(obs.incident_description),
#         "reward": float(reward),
#         "done": bool(done),
#         "info": str(info)
#     }


import requests

BASE_URL = "http://localhost:7860"

def run_task(task_name):
    print(f"[START] task={task_name}", flush=True)

    try:
        # Reset environment
        r = requests.post(f"{BASE_URL}/reset", json={"task_id": task_name})
        obs = r.json()

        total_reward = 0

        for step in range(1, 4):
            action = {"action": "analyze incident"}

            r = requests.post(f"{BASE_URL}/step", json=action)
            result = r.json()

            reward = result.get("reward", 0)
            total_reward += reward

            print(f"[STEP] step={step} reward={reward}", flush=True)

            if result.get("done"):
                break

        print(f"[END] task={task_name} score={total_reward} steps={step}", flush=True)

    except Exception as e:
        print(f"[END] task={task_name} score=0 steps=0 error={str(e)}", flush=True)


run_task("task_1_classify")
run_task("task_2_laws")
run_task("task_3_response")