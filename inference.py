from env.environment import IncidentResponseEnv, Action
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

env = IncidentResponseEnv()
app = FastAPI(root_path="")
from fastapi.responses import JSONResponse

class ActionInput(BaseModel):
    action: str

@app.post("/")
def api_reset():
    obs = env.reset()
    return JSONResponse({
        "observation": str(obs.incident_description),
        "info": str(obs.instructions)
    })

@app.post("/step")
def api_step(input: ActionInput):
    action_obj = Action(content=input.action)
    obs, reward, done, info = env.step(action_obj)

    return JSONResponse({
        "observation": str(obs.incident_description),
        "reward": float(reward),
        "done": bool(done),
        "info": str(info)
    })

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)