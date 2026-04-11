import os
import gradio as gr
from fastapi import FastAPI
from pydantic import BaseModel
from env.environment import IncidentResponseEnv, Action

# 1. Import your UI builder from your app file
# Ensure server/app.py has the build_ui() function available
from server.app import build_ui 

app = FastAPI()
env = IncidentResponseEnv()

class ActionInput(BaseModel):
    action: str

# --- VALIDATOR ENDPOINTS ---

@app.post("/reset")
async def api_reset():
    obs = env.reset()
    print(f"[START] task=incident_response", flush=True)
    return {"observation": str(obs.incident_description), "info": str(obs.instructions)}

@app.post("/step")
async def api_step(input_data: ActionInput):
    action_obj = Action(content=input_data.action)
    obs, reward, done, info = env.step(action_obj)
    
    print(f"[STEP] reward={reward}", flush=True)
    if done:
        print(f"[END] score={reward}", flush=True)
        
    return {"observation": str(obs.incident_description), "reward": float(reward), "done": bool(done)}

# --- UI MOUNTING ---

# 2. Build the Gradio app
demo = build_ui()

# 3. Mount Gradio to the FastAPI app at the root "/"
# This allows you to see the UI when you visit the Space URL
app = gr.mount_gradio_app(app, demo, path="/")