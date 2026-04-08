# 🚨 AI Incident Response Environment

> **OpenEnv RL Hackathon Submission** — A production-grade reinforcement learning environment for AI-assisted cybercrime and legal incident handling.

---

## Overview

The **AI Incident Response Environment** simulates the real-world workflow that cybersecurity analysts and legal teams perform when responding to digital incidents. An RL agent must:

1. **Classify** the incident type (phishing, ransomware, data breach, etc.)
2. **Map applicable laws** (GDPR, HIPAA, CCPA, CFAA, and more)
3. **Generate a structured remediation plan** in JSON format

This is not a toy problem. Every scenario is modeled after real documented incidents, involving realistic legal jurisdictions, attack vectors, and industry contexts.

---

## Motivation

Incident response is time-critical and error-prone. Misclassifying an attack or missing a legal obligation can cost organizations millions and expose them to regulatory penalties. Training AI agents to handle these workflows systematically can:

- Speed up triage by 10x
- Reduce missed legal obligations
- Standardize remediation playbooks
- Assist under-resourced security teams

---

## Environment Architecture

```
incident-env/
├── env/
│   ├── environment.py   # IncidentResponseEnv (OpenEnv-compliant)
│   ├── tasks.py         # Task definitions (Easy / Medium / Hard)
│   └── grader/
│       └── grader.py    # Deterministic scoring functions
├── inference.py         # Baseline inference script (OpenAI client)
├── openenv.yaml         # OpenEnv metadata
├── Dockerfile           # Container definition
├── requirements.txt     # Python dependencies
└── README.md
```

---

## Observation & Action Spaces

### Observation

| Field | Type | Description |
|---|---|---|
| `task_id` | str | Unique task identifier |
| `task_name` | str | Human-readable task name |
| `difficulty` | str | `easy`, `medium`, or `hard` |
| `incident_description` | str | Full natural-language incident report |
| `context` | dict | Metadata (categories, geography, industry) |
| `step` | int | Current step number |
| `max_steps` | int | Episode step limit |
| `instructions` | str | Precise task instructions for the agent |

### Action

| Field | Type | Description |
|---|---|---|
| `content` | str | Agent's free-form text or JSON response |

---

## Tasks

### Task 1 — Easy: Incident Classification

**Scenario:** A user falls victim to a credential-harvesting email and has their bank account accessed.

**Objective:** Classify the incident into exactly one category:
`phishing`, `ransomware`, `ddos`, `insider_threat`, `financial_fraud`, `online_harassment`, `data_breach`

**Grading:**
- `1.0` — Correct primary classification (`phishing`)
- `0.5` — Acceptable alternative (`financial_fraud`)
- `0.0` — Incorrect or verbose response

---

### Task 2 — Medium: Multi-law Mapping

**Scenario:** A former employee exfiltrates 500,000 customer records (PII + financial data) and sells them to a competitor. Customers span US, EU, and India.

**Objective:** Identify all applicable laws from: `GDPR`, `CCPA`, `CFAA`, `IT_ACT_2000`, `HIPAA`, `PCI_DSS`, `SOX`, `ECPA`

**Grading:**
- `0.0–0.6` — Proportion of mandatory laws identified (GDPR, CCPA, CFAA)
- `+0.15` per optional law correctly included (IT_ACT_2000, PCI_DSS)
- `–0.15` per law incorrectly included (HIPAA, SOX)

---

### Task 3 — Hard: Structured Incident Response JSON

**Scenario:** A healthcare startup is hit with ransomware via spear-phishing. Patient records encrypted, $500K ransom demanded, no clean backups, EU and California data involved.

**Objective:** Produce a complete JSON response plan:
```json
{
  "incident_type": "ransomware",
  "laws": ["HIPAA", "GDPR", "CCPA", "CFAA"],
  "actions": [
    "Immediately isolate all affected systems from the network",
    "Engage forensic investigators to preserve evidence",
    "Notify HHS and relevant EU DPAs within 72 hours",
    "Do NOT pay the ransom — contact FBI and CISA",
    "Attempt recovery from last known clean backups",
    "Reset all credentials, especially privileged accounts",
    "Communicate transparently with affected patients"
  ],
  "severity": "critical"
}
```

**Grading (incremental):**
- `+0.20` — Valid JSON with all required keys
- `+0.20` — Correct incident type
- `+0.25` — Required laws (HIPAA + GDPR mandatory, bonus for CCPA/CFAA/HITECH)
- `+0.25` — Actions contain at minimum 4 of: isolate, backup, notify, law enforcement, ransom, forensic, restore, credential
- `+0.10` — Severity is `critical`
- `–0.15` — Severity is wrong

---

## Reward Function

Rewards are **incremental** — the agent receives feedback at each step, not just at completion:

| Component | Reward |
|---|---|
| Correct primary classification | `1.0` |
| Acceptable alternative classification | `0.5` |
| Each required law identified | proportional |
| Bonus optional laws | `+0.15` each |
| Irrelevant laws included | `–0.15` each |
| Valid JSON structure | `+0.20` |
| Correct severity | `+0.10` |
| Empty response | `0.0` |
| Invalid JSON (Task 3) | `0.0–0.10` |

---

## Setup & Usage

### Local

```bash
git clone <repo>
cd incident-env
pip install -r requirements.txt

export HF_TOKEN=your_api_key
export API_BASE_URL=https://api.openai.com/v1  # or your endpoint
export MODEL_NAME=gpt-4.1-mini

python inference.py
```

### Docker

```bash
docker build -t incident-env .

docker run \
  -e HF_TOKEN=your_api_key \
  -e API_BASE_URL=https://api.openai.com/v1 \
  -e MODEL_NAME=gpt-4.1-mini \
  incident-env
```

### Use in Python

```python
from env.environment import IncidentResponseEnv, Action

env = IncidentResponseEnv(task_id="task_1_classify")
obs = env.reset()

print(obs.incident_description)
print(obs.instructions)

action = Action(content="phishing")
obs, reward, done, info = env.step(action)
print(f"Reward: {reward}, Done: {done}")
print(info["grade_details"])
```

---

## Baseline Performance

Tested with `gpt-4.1-mini` at temperature 0.0:

| Task | Difficulty | Avg Reward | Success Rate |
|---|---|---|---|
| incident-classification | Easy | 0.95 | 95% |
| law-mapping | Medium | 0.72 | 70% |
| structured-response | Hard | 0.68 | 65% |

*Baseline scores are reproducible with `temperature=0.0` and fixed task scenarios.*

---

## OpenEnv Compliance

- ✅ Typed `Observation`, `Action` models via Pydantic
- ✅ `step(action)` → `(observation, reward, done, info)`
- ✅ `reset()` → initial observation
- ✅ `state()` → current environment state
- ✅ `openenv.yaml` with full metadata
- ✅ 3 tasks with deterministic graders
- ✅ Incremental reward function
- ✅ Baseline `inference.py` using OpenAI client
- ✅ Docker-deployable
- ✅ Tagged `openenv`

---

## Hardware Requirements

Runs comfortably within:
- **2 vCPU**
- **8 GB RAM**

No GPU required. No local model weights. Pure API-based inference.

---

## License

MIT
