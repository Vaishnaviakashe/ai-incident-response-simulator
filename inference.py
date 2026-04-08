from env.environment import IncidentResponseEnv, Action
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import JSONResponse
import uvicorn

env = IncidentResponseEnv()
app = FastAPI()

class ActionInput(BaseModel):
    action: str

@app.get("/")
def root():
    return {"message": "API is running"}

@app.post("/")
def root_post():
    obs = env.reset()
    return {
        "observation": str(obs.incident_description),
        "info": str(obs.instructions)
    }

@app.post("/reset")
def api_reset():
    obs = env.reset()
    return {
        "observation": str(obs.incident_description),
        "info": str(obs.instructions)
    }

@app.post("/step")
def api_step(input: ActionInput):
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