import os
from fastapi import FastAPI
from pydantic import BaseModel
from env.environment import IncidentResponseEnv, Action

app = FastAPI()
env = IncidentResponseEnv()

class ActionInput(BaseModel):
    action: str

@app.get("/")
async def health():
    return {"status": "ok"}

@app.post("/reset")
async def api_reset():
    obs = env.reset()
    # Validator needs to see this in logs
    print(f"[START] task=incident_response", flush=True)
    return {"observation": str(obs.incident_description), "info": str(obs.instructions)}

@app.post("/step")
async def api_step(input_data: ActionInput):
    action_obj = Action(content=input_data.action)
    obs, reward, done, info = env.step(action_obj)
    
    # Validator needs to see these in logs
    print(f"[STEP] reward={reward}", flush=True)
    if done:
        print(f"[END] score={reward}", flush=True)
        
    return {"observation": str(obs.incident_description), "reward": float(reward), "done": bool(done)}