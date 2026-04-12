import os
import sys
import gradio as gr
from fastapi import FastAPI
from pydantic import BaseModel
from env.environment import IncidentResponseEnv, Action
from server.app import build_ui 

app = FastAPI()
env = IncidentResponseEnv()

class ActionInput(BaseModel):
    action: str

# Helper function to write directly to system stdout
def force_log(message):
    sys.stdout.write(message + "\n")
    sys.stdout.flush()

@app.post("/reset")
async def api_reset():
    obs = env.reset()
    # Direct write to bypass all logging interference
    force_log("[START] task=incident_response")
    return {"observation": str(obs.incident_description), "info": str(obs.instructions)}

@app.post("/step")
async def api_step(input_data: ActionInput):
    action_obj = Action(content=input_data.action)
    obs, reward, done, info = env.step(action_obj)
    
    force_log(f"[STEP] reward={reward}")
    
    if done:
        force_log(f"[END] score={reward}")
        
    return {
        "observation": str(obs.incident_description), 
        "reward": float(reward), 
        "done": bool(done)
    }

# UI Mounting
demo = build_ui()
app = gr.mount_gradio_app(app, demo, path="/")