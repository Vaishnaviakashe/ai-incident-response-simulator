
"""
Task definitions for the AI Incident Response Environment.
6 scenarios across 3 difficulty levels (2 per level).
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class Task:
    task_id: str
    name: str
    difficulty: str
    incident_description: str
    instructions: str
    context: Dict[str, Any]
    expected_output: Dict[str, Any]
    max_steps: int = 5
    scenario_title: str = ""


TASK_1A = Task(
    task_id="task_1_classify",
    name="incident-classification",
    difficulty="easy",
    scenario_title="Bank Phishing Attack",
    incident_description=(
        "A user reports receiving an email claiming to be from their bank. "
        "The email asked them to click a link and enter their account credentials. "
        "After clicking, their account was accessed by an unknown party from a foreign IP address. "
        "Funds totaling $4,200 were transferred without authorization within 3 hours."
    ),
    instructions=(
        "Classify this incident into exactly ONE of the following categories:\n"
        "- phishing\n- ransomware\n- ddos\n- insider_threat\n"
        "- financial_fraud\n- online_harassment\n- data_breach\n\n"
        "Respond with ONLY the category name, lowercase, no punctuation."
    ),
    context={"categories": ["phishing","ransomware","ddos","insider_threat","financial_fraud","online_harassment","data_breach"]},
    expected_output={"incident_type": "phishing", "acceptable_alternatives": ["financial_fraud"]},
    max_steps=3,
)

TASK_1B = Task(
    task_id="task_1b_classify",
    name="incident-classification-ddos",
    difficulty="easy",
    scenario_title="E-Commerce DDoS Attack",
    incident_description=(
        "An e-commerce platform reports their website became completely unreachable "
        "during a Black Friday sale. Network logs show 2.3 million requests per second "
        "originating from over 140 countries simultaneously. The attack lasted 6 hours, "
        "causing an estimated $800,000 in lost sales. No data was accessed or stolen."
    ),
    instructions=(
        "Classify this incident into exactly ONE of the following categories:\n"
        "- phishing\n- ransomware\n- ddos\n- insider_threat\n"
        "- financial_fraud\n- online_harassment\n- data_breach\n\n"
        "Respond with ONLY the category name, lowercase, no punctuation."
    ),
    context={"categories": ["phishing","ransomware","ddos","insider_threat","financial_fraud","online_harassment","data_breach"]},
    expected_output={"incident_type": "ddos", "acceptable_alternatives": []},
    max_steps=3,
)

TASK_2A = Task(
    task_id="task_2_laws",
    name="law-mapping",
    difficulty="medium",
    scenario_title="Insider Data Exfiltration — Multi-Jurisdiction",
    incident_description=(
        "A mid-sized e-commerce company discovered that a former employee, before resigning, "
        "exfiltrated the entire customer database (500,000 records) including names, email addresses, "
        "credit card numbers (partial), and purchase history. The employee sold "
        "this data to a competitor. The breach was detected 45 days after it occurred. "
        "Customers are based in the US, EU, and India."
    ),
    instructions=(
        "Identify ALL applicable laws and regulations for this incident.\n"
        "Choose ONLY from this list:\n"
        "GDPR, CCPA, CFAA, IT_ACT_2000, HIPAA, PCI_DSS, SOX, ECPA\n\n"
        "Respond with a comma-separated list, e.g.: GDPR,CCPA,CFAA\n"
        "Order does not matter. Only include laws that clearly apply."
    ),
    context={
        "available_laws": ["GDPR","CCPA","CFAA","IT_ACT_2000","HIPAA","PCI_DSS","SOX","ECPA"],
        "geography": ["US","EU","India"],
        "data_types": ["PII","financial","purchase_history"],
    },
    expected_output={
        "laws": ["GDPR","CCPA","CFAA","IT_ACT_2000","PCI_DSS"],
        "minimum_required": ["GDPR","CFAA","CCPA"],
        "optional_credit": ["IT_ACT_2000","PCI_DSS"],
        "should_not_include": ["HIPAA","SOX"],
    },
    max_steps=3,
)

TASK_2B = Task(
    task_id="task_2b_laws",
    name="law-mapping-financial",
    difficulty="medium",
    scenario_title="CEO Fraud — Wire Transfer Scam",
    incident_description=(
        "A US-based manufacturing firm's CFO received an email appearing to be from the CEO "
        "instructing an urgent $2.1M wire transfer to a foreign account for a confidential acquisition. "
        "The email domain was spoofed. The transfer was completed before fraud was detected. "
        "The company is publicly traded on NASDAQ. Employee email records were also accessed "
        "during the attack via compromised CFO credentials."
    ),
    instructions=(
        "Identify ALL applicable laws and regulations for this incident.\n"
        "Choose ONLY from this list:\n"
        "GDPR, CCPA, CFAA, IT_ACT_2000, HIPAA, PCI_DSS, SOX, ECPA, WIRE_FRAUD_ACT\n\n"
        "Respond with a comma-separated list, e.g.: CFAA,SOX\n"
        "Order does not matter. Only include laws that clearly apply."
    ),
    context={
        "available_laws": ["GDPR","CCPA","CFAA","IT_ACT_2000","HIPAA","PCI_DSS","SOX","ECPA","WIRE_FRAUD_ACT"],
        "geography": ["US"],
        "company_type": "publicly_traded",
        "data_types": ["financial_records","email_communications"],
    },
    expected_output={
        "laws": ["CFAA","SOX","ECPA","WIRE_FRAUD_ACT"],
        "minimum_required": ["CFAA","SOX","WIRE_FRAUD_ACT"],
        "optional_credit": ["ECPA"],
        "should_not_include": ["HIPAA","GDPR","IT_ACT_2000"],
    },
    max_steps=3,
)

TASK_3A = Task(
    task_id="task_3_response",
    name="structured-response",
    difficulty="hard",
    scenario_title="Healthcare Ransomware + Dark Web Leak Threat",
    incident_description=(
        "A healthcare startup's internal Slack workspace was compromised. An attacker used stolen "
        "credentials via a spear-phishing campaign targeting the CTO. Once inside, they "
        "deployed ransomware encrypting 3TB of patient records and internal communications. "
        "A ransom note demands $500,000 in Bitcoin within 72 hours or data will be published "
        "on a dark web leak site. The company serves patients in California and has EU-based "
        "clinical trial partners. No backups verified clean. Staff cannot access any internal systems."
    ),
    instructions=(
        "Produce a complete incident response plan as a valid JSON object with EXACTLY these keys:\n\n"
        '{"incident_type": "<string>", "laws": ["<law1>", ...], "actions": ["<action1>", ...], "severity": "<low|medium|high|critical>"}\n\n'
        "- incident_type: single string\n"
        "- laws: minimum 3 applicable laws\n"
        "- actions: minimum 5 concrete prioritized response steps\n"
        "- severity: choose the appropriate level\n\n"
        "Return ONLY valid JSON. No markdown, no explanation."
    ),
    context={
        "industry": "healthcare",
        "geography": ["California","EU"],
        "data_types": ["patient_records","PHI","communications"],
        "threat_type": "ransomware + phishing",
        "ransom_demanded": True,
        "backups_clean": False,
    },
    expected_output={
        "incident_type": "ransomware",
        "acceptable_incident_types": ["ransomware","ransomware_attack","data_breach_ransomware"],
        "required_laws": ["HIPAA","GDPR"],
        "bonus_laws": ["CCPA","CFAA","HITECH"],
        "required_actions_keywords": [
            "isolate","backup","notify","law enforcement","ransom",
            "forensic","restore","credential","patch","communicate"
        ],
        "minimum_actions_keywords_required": 4,
        "severity": "critical",
    },
    max_steps=5,
)

TASK_3B = Task(
    task_id="task_3b_response",
    name="structured-response-supply-chain",
    difficulty="hard",
    scenario_title="SolarWinds-style Supply Chain Attack",
    incident_description=(
        "A government contractor discovered that a software update pushed by a third-party vendor "
        "was trojaned with malware. The malicious update was silently installed on 47 internal "
        "workstations over 3 months before detection. Attackers had persistent access to classified "
        "project documents, network topology maps, and VPN credentials. "
        "The contractor handles defense contracts for the US Department of Defense. "
        "Affected systems include air-gapped networks bridged via an infected laptop."
    ),
    instructions=(
        "Produce a complete incident response plan as a valid JSON object with EXACTLY these keys:\n\n"
        '{"incident_type": "<string>", "laws": ["<law1>", ...], "actions": ["<action1>", ...], "severity": "<low|medium|high|critical>"}\n\n'
        "- incident_type: single string describing the attack\n"
        "- laws: minimum 3 applicable laws or compliance frameworks\n"
        "- actions: minimum 6 concrete prioritized response steps\n"
        "- severity: appropriate level for a nation-state level attack\n\n"
        "Return ONLY valid JSON. No markdown, no explanation."
    ),
    context={
        "industry": "defense_contractor",
        "geography": ["US"],
        "data_types": ["classified_documents","network_maps","credentials"],
        "threat_type": "supply_chain + APT",
        "attacker_persistence_months": 3,
        "air_gap_bridged": True,
    },
    expected_output={
        "incident_type": "supply_chain_attack",
        "acceptable_incident_types": [
            "supply_chain_attack","supply_chain","apt","advanced_persistent_threat",
            "supply_chain_compromise","trojan","malware"
        ],
        "required_laws": ["CFAA","DFARS"],
        "bonus_laws": ["NIST_800_171","CMMC","FISMA","EO_14028"],
        "required_actions_keywords": [
            "isolate","forensic","vendor","notify","credential",
            "audit","patch","monitor","classify","dod","cisa"
        ],
        "minimum_actions_keywords_required": 4,
        "severity": "critical",
    },
    max_steps=5,
)


TASKS: List[Task] = [TASK_1A, TASK_1B, TASK_2A, TASK_2B, TASK_3A, TASK_3B]
PRIMARY_TASKS: List[Task] = [TASK_1A, TASK_2A, TASK_3A]
TASK_MAP: Dict[str, Task] = {t.task_id: t for t in TASKS}
