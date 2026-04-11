import os
import gradio as gr
from fastapi import FastAPI
from pydantic import BaseModel
from env.environment import IncidentResponseEnv, Action
from server.app import build_ui 

app = FastAPI()
env = IncidentResponseEnv()

class ActionInput(BaseModel):
    action: str

# --- VALIDATOR ENDPOINTS ---

@app.post("/reset")
async def api_reset():
    obs = env.reset()
    # MANDATORY: flush=True ensures the validator sees this instantly
    print(f"[START] task=incident_response", flush=True)
    return {"observation": str(obs.incident_description), "info": str(obs.instructions)}

@app.post("/step")
async def api_step(input_data: ActionInput):
    action_obj = Action(content=input_data.action)
    obs, reward, done, info = env.step(action_obj)
    
    # MANDATORY: Every log line must be flushed
    print(f"[STEP] reward={reward}", flush=True)
    
    if done:
        print(f"[END] score={reward}", flush=True)
        
    return {
        "observation": str(obs.incident_description), 
        "reward": float(reward), 
        "done": bool(done)
    }

# --- UI MOUNTING ---
demo = build_ui()
app = gr.mount_gradio_app(app, demo, path="/")