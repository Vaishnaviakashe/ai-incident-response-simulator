"""
AI Incident Response Environment
OpenEnv-compliant RL environment for cybercrime and legal incident handling.
"""

from __future__ import annotations
import json
from typing import Any, Dict, Optional, Tuple
from pydantic import BaseModel, Field
from env.tasks import TASKS, Task
from grader.grader import grade_action


class Observation(BaseModel):
    task_id: str
    task_name: str
    difficulty: str
    incident_description: str
    context: Dict[str, Any] = Field(default_factory=dict)
    step: int = 0
    max_steps: int = 5
    instructions: str = ""


class Action(BaseModel):
    content: str  # raw string or JSON string from agent


class StepResult(BaseModel):
    observation: Observation
    reward: float
    done: bool
    info: Dict[str, Any] = Field(default_factory=dict)


class IncidentResponseEnv:
    """
    OpenEnv-compliant environment for AI Incident Response.
    """

    def __init__(self, task_id: Optional[str] = None):
        self.task_id = task_id
        self._task: Optional[Task] = None
        self._step_count = 0
        self._done = False
        self._last_observation: Optional[Observation] = None
        self._rewards: list[float] = []

    # ------------------------------------------------------------------ #
    # OpenEnv Interface                                                    #
    # ------------------------------------------------------------------ #

    def reset(self) -> Observation:
        """Reset the environment and return the initial observation."""
        task = self._select_task()
        self._task = task
        self._step_count = 0
        self._done = False
        self._rewards = []

        obs = Observation(
            task_id=task.task_id,
            task_name=task.name,
            difficulty=task.difficulty,
            incident_description=task.incident_description,
            context=task.context,
            step=0,
            max_steps=task.max_steps,
            instructions=task.instructions,
        )
        self._last_observation = obs
        return obs

    def step(self, action: Action) -> Tuple[Observation, float, bool, Dict[str, Any]]:
        """
        Execute one step in the environment.
        Returns: (observation, reward, done, info)
        """
        if self._done:
            raise RuntimeError("Episode is done. Call reset() to start a new episode.")
        if self._task is None:
            raise RuntimeError("Environment not initialized. Call reset() first.")

        self._step_count += 1

        # Grade the action
        grade_result = grade_action(
            task=self._task,
            action_content=action.content,
            step=self._step_count,
        )

        reward = grade_result["reward"]
        self._rewards.append(reward)

        # Determine done
        done = (
            grade_result.get("is_correct", False)
            or self._step_count >= self._task.max_steps
        )
        
        if reward > 0.7:
            done = True
            
        if len(self._rewards) >= 3:
            if self._rewards[-1] == self._rewards[-2] == self._rewards[-3]:
                done = True
        self._done = done
        
        

        # Build next observation
        obs = Observation(
            task_id=self._task.task_id,
            task_name=self._task.name,
            difficulty=self._task.difficulty,
            incident_description=self._task.incident_description,
            context=self._task.context,
            step=self._step_count,
            max_steps=self._task.max_steps,
            instructions=self._task.instructions,
        )
        self._last_observation = obs

        info = {
        "grade_details": grade_result,
        "cumulative_reward": sum(self._rewards),
        "steps_taken": self._step_count,
        "last_action_error": grade_result.get("error"),
        "reason": "Correct response" if grade_result.get("is_correct") else "Partial/Incorrect response",
    }

        return obs, reward, done, info

    def state(self) -> Dict[str, Any]:
        """Return the current environment state."""
        return {
            "task_id": self._task.task_id if self._task else None,
            "step": self._step_count,
            "done": self._done,
            "rewards": self._rewards,
            "cumulative_reward": sum(self._rewards),
            "observation": self._last_observation.model_dump() if self._last_observation else None,
        }

    def close(self):
        """Clean up resources."""
        pass

    # ------------------------------------------------------------------ #
    # Helpers                                                              #
    # ------------------------------------------------------------------ #

    def _select_task(self) -> Task:
        if self.task_id:
            for t in TASKS:
                if t.task_id == self.task_id:
                    return t
            raise ValueError(f"Unknown task_id: {self.task_id}")
        # default: first task
        return TASKS[0]

    @property
    def all_tasks(self):
        return TASKS


