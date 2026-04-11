import requests

BASE_URL = "http://localhost:7860"

def run_task(task_name):
    print(f"[START] task={task_name}", flush=True)

    try:
        # Reset environment
        r = requests.post(f"{BASE_URL}/reset", json={"task_id": task_name})
        obs = r.json()

        total_reward = 0

        for step in range(1, 4):
            action = {"action": "analyze incident"}

            r = requests.post(f"{BASE_URL}/step", json=action)
            result = r.json()

            reward = result.get("reward", 0)
            total_reward += reward

            print(f"[STEP] step={step} reward={reward}", flush=True)

            if result.get("done"):
                break

        print(f"[END] task={task_name} score={total_reward} steps={step}", flush=True)

    except Exception as e:
        print(f"[END] task={task_name} score=0 steps=0 error={str(e)}", flush=True)


run_task("task_1_classify")
run_task("task_2_laws")
run_task("task_3_response")