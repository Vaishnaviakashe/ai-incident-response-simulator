import os
from fastapi import FastAPI, Request
from pydantic import BaseModel
from env.environment import IncidentResponseEnv, Action

app = FastAPI()
env = IncidentResponseEnv()
HF_TOKEN = os.getenv("HF_TOKEN")

class ActionInput(BaseModel):
    action: str

@app.get("/")
async def root():
    return {"status": "alive", "message": "OpenEnv API"}

@app.post("/reset")
async def api_reset():
    obs = env.reset()
    # CRITICAL: Print [START] so the validator knows the task began
    print(f"[START] task={getattr(env, 'task_id', 'incident_task')}", flush=True)
    return {
        "observation": str(obs.incident_description),
        "info": str(obs.instructions)
    }

@app.post("/step")
async def api_step(input: ActionInput):
    action_obj = Action(content=input.action)
    obs, reward, done, info = env.step(action_obj)
    
    # CRITICAL: Print [STEP] for every action taken
    step_num = info.get("step_count", 1) 
    print(f"[STEP] step={step_num} reward={reward}", flush=True)
    
    if done:
        # CRITICAL: Print [END] when the task is finished
        total_reward = info.get("total_reward", reward)
        print(f"[END] task={getattr(env, 'task_id', 'incident_task')} score={total_reward} steps={step_num}", flush=True)
        
    return {
        "observation": str(obs.incident_description),
        "reward": float(reward),
        "done": bool(done),
        "info": str(info)
    }