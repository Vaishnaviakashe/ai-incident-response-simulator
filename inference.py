from env.environment import IncidentResponseEnv, Action

env = IncidentResponseEnv()

def run_task(task_name):
    print(f"[START] task={task_name}", flush=True)

    try:
        obs = env.reset()

        total_reward = 0
        step = 0

        for step in range(1, 4):
            action = Action(content="analyze incident")

            obs, reward, done, info = env.step(action)

            total_reward += reward

            print(f"[STEP] step={step} reward={reward}", flush=True)

            if done:
                break

        print(f"[END] task={task_name} score={total_reward} steps={step}", flush=True)

    except Exception as e:
        print(f"[END] task={task_name} score=0 steps=0 error={str(e)}", flush=True)


# RUN DIRECTLY
run_task("task_1_classify")
run_task("task_2_laws")
run_task("task_3_response")