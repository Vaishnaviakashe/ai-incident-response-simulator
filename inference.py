import os
import sys
import gradio as gr
from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
from env.environment import IncidentResponseEnv, Action
from server.app import build_ui 

app = FastAPI()
env = IncidentResponseEnv()

class ActionInput(BaseModel):
    action: str

# --- API ENDPOINTS ---
@app.post("/reset")
async def api_reset():
    obs = env.reset()
    return {"observation": str(obs.incident_description)}

@app.post("/step")
async def api_step(input_data: ActionInput):
    action_obj = Action(content=input_data.action)
    obs, reward, done, info = env.step(action_obj)
    return {"reward": float(reward), "done": bool(done)}



# --- UI SETUP ---
demo = build_ui()
app = gr.mount_gradio_app(app, demo, path="/")

def run_eval_tasks():
    # 1. Grab the keys the validator provides automatically
    # DO NOT hardcode a string here. Leave it as os.environ.get
    api_key = os.environ.get("API_KEY")
    base_url = os.environ.get("API_BASE_URL")
    model_name = os.environ.get("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")

    # 2. Initialize the client using their Proxy
    if not api_key or not base_url:
        # Fallback for local testing only
        client = OpenAI(api_key="your_local_token", base_url="https://api-inference.huggingface.co/v1")
    else:
        client = OpenAI(api_key=api_key, base_url=base_url)

    tasks = ["task_1_classify", "task_2_laws", "task_3_response"]
    
    for task_name in tasks:
        sys.stdout.write(f"[START] task={task_name}\n")
        sys.stdout.flush()
        try:
            env = IncidentResponseEnv(task_id=task_name)
            obs = env.reset()

            # 3. The Actual Proxy Call
            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": str(obs.incident_description)}]
            )
            answer = response.choices[0].message.content

            # 4. Use the model's answer to take the step
            obs, reward, done, info = env.step(Action(content=answer))

            sys.stdout.write(f"[STEP] step=1 reward={float(reward)}\n")
            sys.stdout.write(f"[END] task={task_name} score={float(reward)} steps=1\n")
        except Exception as e:
            sys.stdout.write(f"[END] task={task_name} score=0 steps=0 error={str(e)}\n")
        sys.stdout.flush()

# --- THE FIX FOR "ADDRESS ALREADY IN USE" ---
if __name__ == "__main__":
    # When the validator runs 'python inference.py', it ONLY does this:
    # tasks = ["task_1_classify", "task_2_laws", "task_3_response"]
    # for task_name in tasks:
    #     sys.stdout.write(f"[START] task={task_name}\n")
    #     sys.stdout.write(f"[STEP] step=1 reward=1.0\n")
    #     sys.stdout.write(f"[END] task={task_name} score=1.0 steps=1\n")
    # sys.stdout.flush()
    
    run_eval_tasks()
    # WE DO NOT CALL uvicorn.run() HERE. 
    # This prevents the "Address already in use" error.