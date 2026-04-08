"""
Deterministic graders for each task in the AI Incident Response Environment.
Returns reward in [0.0, 1.0] with incremental partial credit.
"""

from __future__ import annotations
import json
import re
from typing import Any, Dict


def grade_action(task, action_content: str, step: int) -> Dict[str, Any]:
    """
    Route grading to the appropriate task grader.
    Always returns a dict with: reward, is_correct, error, details
    """
    action_content = (action_content or "").strip()

    if not action_content:
        return _make_result(0.0, False, "empty_response", {"note": "Empty action received"})

    try:
        if task.task_id == "task_1_classify":
            return _grade_task1(task, action_content)
        elif task.task_id == "task_2_laws":
            return _grade_task2(task, action_content)
        elif task.task_id == "task_3_response":
            return _grade_task3(task, action_content)
        else:
            return _make_result(0.0, False, "unknown_task", {})
    except Exception as e:
        return _make_result(0.0, False, str(e), {"exception": True})


# ─────────────────────────────────────────────────────────────────────────────
# TASK 1 GRADER — Single-label Classification
# ─────────────────────────────────────────────────────────────────────────────

def _grade_task1(task, content: str) -> Dict[str, Any]:
    """
    Reward structure:
      1.0 — exact match with primary answer
      0.5 — acceptable alternative
      0.0 — wrong or irrelevant
    Penalty: -0.1 for verbose / multi-word responses (should be a single word)
    """
    normalized = content.lower().strip().rstrip(".")
    expected = task.expected_output

    # penalize if agent returned a long response instead of single word
    verbose_penalty = 0.0
    if len(normalized.split()) > 3:
        verbose_penalty = 0.1

    if normalized == expected["incident_type"]:
        reward = max(0.0, 1.0 - verbose_penalty)
        return _make_result(reward, True, None, {
            "matched": "primary",
            "expected": expected["incident_type"],
            "got": normalized,
        })

    if normalized in [a.lower() for a in expected.get("acceptable_alternatives", [])]:
        reward = max(0.0, 0.5 - verbose_penalty)
        return _make_result(reward, True, None, {
            "matched": "alternative",
            "expected": expected["incident_type"],
            "got": normalized,
        })

    return _make_result(0.0, False, None, {
        "matched": "none",
        "expected": expected["incident_type"],
        "got": normalized,
    })


# ─────────────────────────────────────────────────────────────────────────────
# TASK 2 GRADER — Multi-label Law Mapping
# ─────────────────────────────────────────────────────────────────────────────

def _grade_task2(task, content: str) -> Dict[str, Any]:
    """
    Reward structure:
      Base: proportion of minimum_required laws correctly identified (0.0–0.6)
      Bonus: +0.1 per optional_credit law, up to 0.3
      Penalty: -0.15 per law from should_not_include
      Final reward clamped to [0.0, 1.0]
    """
    expected = task.expected_output
    minimum_required = [l.upper() for l in expected["minimum_required"]]
    optional_credit = [l.upper() for l in expected.get("optional_credit", [])]
    should_not_include = [l.upper() for l in expected.get("should_not_include", [])]

    # Parse submitted laws
    submitted = _parse_law_list(content)

    # Calculate scores
    required_matched = [l for l in minimum_required if l in submitted]
    optional_matched = [l for l in optional_credit if l in submitted]
    wrong_included = [l for l in should_not_include if l in submitted]

    base_score = len(required_matched) / len(minimum_required) * 0.6
    bonus = min(len(optional_matched) * 0.15, 0.4)
    penalty = len(wrong_included) * 0.15

    reward = max(0.0, min(1.0, base_score + bonus - penalty))
    is_correct = len(required_matched) == len(minimum_required) and len(wrong_included) == 0

    return _make_result(reward, is_correct, None, {
        "required_matched": required_matched,
        "optional_matched": optional_matched,
        "wrong_included": wrong_included,
        "submitted": list(submitted),
        "base_score": round(base_score, 3),
        "bonus": round(bonus, 3),
        "penalty": round(penalty, 3),
    })


def _parse_law_list(content: str) -> set:
    """Parse comma-separated law names from agent response."""
    # Handle JSON array format too
    content = content.strip()
    if content.startswith("["):
        try:
            items = json.loads(content)
            return {str(i).upper().strip() for i in items}
        except Exception:
            pass
    parts = re.split(r"[,\s\n]+", content)
    return {p.upper().strip().rstrip(".") for p in parts if p.strip()}


# ─────────────────────────────────────────────────────────────────────────────
# TASK 3 GRADER — Full Structured Response JSON
# ─────────────────────────────────────────────────────────────────────────────

def _grade_task3(task, content: str) -> Dict[str, Any]:
    """
    Reward breakdown (incremental):
      0.20 — Valid JSON with all required keys
      0.20 — Correct incident_type
      0.25 — Required laws present (HIPAA + GDPR mandatory)
      0.25 — Enough actions with relevant keywords
      0.10 — Correct severity ('critical')
      Total max: 1.0
    Penalties:
      -0.1  — Extra keys present (sloppy output)
      -0.15 — severity is not 'critical'
    """
    expected = task.expected_output
    details = {}
    reward = 0.0
    errors = []

    # Step 1: Parse JSON
    parsed = _extract_json(content)
    if parsed is None:
        return _make_result(0.0, False, "invalid_json", {"raw": content[:200]})

    reward += 0.20
    details["json_valid"] = True

    required_keys = {"incident_type", "laws", "actions", "severity"}
    present_keys = set(parsed.keys())
    if not required_keys.issubset(present_keys):
        missing = required_keys - present_keys
        errors.append(f"missing_keys:{missing}")
        return _make_result(0.10, False, ",".join(errors), details)

    # Step 2: incident_type
    incident_type = str(parsed.get("incident_type", "")).lower().strip()
    acceptable = [t.lower() for t in expected["acceptable_incident_types"]]
    if incident_type in acceptable:
        reward += 0.20
        details["incident_type_correct"] = True
    else:
        details["incident_type_correct"] = False
        details["got_incident_type"] = incident_type

    # Step 3: laws
    submitted_laws = {str(l).upper().strip() for l in (parsed.get("laws") or [])}
    required_laws = [l.upper() for l in expected["required_laws"]]
    bonus_laws = [l.upper() for l in expected.get("bonus_laws", [])]

    required_law_hits = [l for l in required_laws if l in submitted_laws]
    bonus_law_hits = [l for l in bonus_laws if l in submitted_laws]

    law_score = (len(required_law_hits) / len(required_laws)) * 0.20
    law_bonus = min(len(bonus_law_hits) * 0.025, 0.05)
    reward += law_score + law_bonus
    details["required_laws_matched"] = required_law_hits
    details["bonus_laws_matched"] = bonus_law_hits

    # Step 4: actions
    actions = parsed.get("actions") or []
    if isinstance(actions, list) and len(actions) >= 5:
        all_actions_text = " ".join(str(a).lower() for a in actions)
        kw_required = expected["required_actions_keywords"]
        kw_min = expected["minimum_actions_keywords_required"]
        kw_hits = [kw for kw in kw_required if kw.lower() in all_actions_text]
        action_score = min(len(kw_hits) / kw_min, 1.0) * 0.25
        reward += action_score
        details["action_keywords_found"] = kw_hits
        details["action_count"] = len(actions)
    else:
        details["action_count"] = len(actions) if isinstance(actions, list) else 0
        details["actions_insufficient"] = True

    # Step 5: severity
    severity = str(parsed.get("severity", "")).lower().strip()
    if severity == expected["severity"]:
        reward += 0.10
        details["severity_correct"] = True
    else:
        reward -= 0.15
        details["severity_correct"] = False
        details["got_severity"] = severity

    reward = max(0.0, min(1.0, reward))
    is_correct = reward >= 0.75

    return _make_result(round(reward, 4), is_correct, ",".join(errors) or None, details)


def _extract_json(content: str) -> Any:
    """Try to extract a JSON object from the agent response."""
    content = content.strip()
    # Strip markdown code fences
    content = re.sub(r"^```(?:json)?\s*", "", content)
    content = re.sub(r"\s*```$", "", content)
    content = content.strip()
    try:
        return json.loads(content)
    except Exception:
        # Try to find JSON object in the string
        match = re.search(r"\{.*\}", content, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except Exception:
                return None
    return None


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _make_result(
    reward: float,
    is_correct: bool,
    error: Any,
    details: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "reward": round(float(reward), 4),
        "is_correct": is_correct,
        "error": error,
        "details": details,
    }
