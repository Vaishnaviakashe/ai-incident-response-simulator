import os

from fastapi import FastAPI, Request
from pydantic import BaseModel
from env.environment import IncidentResponseEnv, Action
import uvicorn

app = FastAPI()
env = IncidentResponseEnv()
HF_TOKEN = os.getenv("HF_TOKEN")

class ActionInput(BaseModel):
    action: str

# 1. Catch-all for the ROOT (GET and POST)
@app.get("/")
async def root():
    return {"status": "alive", "message": "OpenEnv API"}

@app.post("/")
async def root_post():
    obs = env.reset()
    return {
        "observation": str(obs.incident_description),
        "info": str(obs.instructions)
    }

# 2. Specific RESET endpoint
@app.post("/reset")
async def api_reset():
    obs = env.reset()
    return {
        "observation": str(obs.incident_description),
        "info": str(obs.instructions)
    }

# 3. STEP endpoint
@app.post("/step")
async def api_step(input: ActionInput):
    action_obj = Action(content=input.action)
    obs, reward, done, info = env.step(action_obj)
    return {
        "observation": str(obs.incident_description),
        "reward": float(reward),
        "done": bool(done),
        "info": str(info)
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)