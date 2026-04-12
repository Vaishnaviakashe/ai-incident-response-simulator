import os
import logging
import gradio as gr
from fastapi import FastAPI
from pydantic import BaseModel
from env.environment import IncidentResponseEnv, Action
from server.app import build_ui 

# Setup system-level logging to ensure stdout is captured
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("validator")

app = FastAPI()
env = IncidentResponseEnv()

class ActionInput(BaseModel):
    action: str

# --- VALIDATOR ENDPOINTS ---

@app.post("/reset")
async def api_reset():
    obs = env.reset()
    # Use logger.info to force output into the container's primary stdout stream
    logger.info("[START] task=incident_response")
    return {"observation": str(obs.incident_description), "info": str(obs.instructions)}

@app.post("/step")
async def api_step(input_data: ActionInput):
    action_obj = Action(content=input_data.action)
    obs, reward, done, info = env.step(action_obj)
    
    # Precise formatting required by Phase 2 parsing
    logger.info(f"[STEP] reward={reward}")
    
    if done:
        logger.info(f"[END] score={reward}")
        
    return {
        "observation": str(obs.incident_description), 
        "reward": float(reward), 
        "done": bool(done)
    }

# --- UI MOUNTING ---
demo = build_ui()
app = gr.mount_gradio_app(app, demo, path="/")