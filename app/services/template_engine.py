from __future__ import annotations
from dataclasses import dataclass
from datetime import date, timedelta
from typing import List, Dict, Any

# Embedded templates for executive mock (replace with YAML later)
TEMPLATES: Dict[str, Dict[str, Any]] = {
    "general_newgrad": {
        "tasks": [
            {"owner": "employee", "title": "Complete HR paperwork", "desc": "Fill in onboarding forms and submit required documents.", "offset": 0},
            {"owner": "employee", "title": "Read company handbook", "desc": "Review key policies and working norms.", "offset": 2},
            {"owner": "manager", "title": "Set up first-week agenda", "desc": "Align meetings, buddy assignment, and access requests.", "offset": -3},
        ],
        "plan": {
            "employee": {
                "day30": "Understand team mission, tools, and workflows. Deliver a small starter task.",
                "day60": "Own a scoped workstream end-to-end. Start proposing improvements.",
                "day90": "Operate independently on core responsibilities. Identify growth goals with manager."
            },
            "manager": {
                "day30": "Set weekly 1:1 cadence; ensure environment setup; clarify expectations.",
                "day60": "Review progress vs role expectations; assign a medium-sized project.",
                "day90": "Performance checkpoint and growth plan; calibrate responsibilities."
            }
        }
    },
    "general_mid": {
        "tasks": [
            {"owner": "employee", "title": "Confirm role expectations", "desc": "Align your 30/60/90-day objectives with the manager.", "offset": 0},
            {"owner": "manager", "title": "Introduce key stakeholders", "desc": "Arrange introductions to cross-functional partners.", "offset": 3},
        ],
        "plan": {
            "employee": {
                "day30": "Map stakeholders, understand current projects, deliver quick wins.",
                "day60": "Lead a key initiative and share progress updates.",
                "day90": "Drive measurable impact and propose next-quarter roadmap."
            },
            "manager": {
                "day30": "Clarify authority/decision boundaries; provide context and priorities.",
                "day60": "Remove blockers and validate impact metrics.",
                "day90": "Set next goals and confirm long-term ownership areas."
            }
        }
    },
    "eng_newgrad": {
        "tasks": [
            {"owner": "employee", "title": "Set up dev environment", "desc": "Install required tools, access repos, run the project locally.", "offset": 0},
            {"owner": "employee", "title": "Complete security training", "desc": "Finish required security modules and acknowledge policies.", "offset": 7},
            {"owner": "manager", "title": "Assign onboarding starter ticket", "desc": "Pick a well-scoped ticket suitable for first 2 weeks.", "offset": 1},
        ],
        "plan": {
            "employee": {
                "day30": "Ship first small PR and understand the deployment flow.",
                "day60": "Own a feature slice and participate in code reviews.",
                "day90": "Become dependable on a component; contribute to design discussions."
            },
            "manager": {
                "day30": "Ensure access + environment; set mentorship plan.",
                "day60": "Expand responsibilities; ensure feedback loop.",
                "day90": "Evaluate readiness for deeper ownership if applicable."
            }
        }
    },
    "cs_mid": {
        "tasks": [
            {"owner": "employee", "title": "Review support playbook", "desc": "Learn escalation policies and standard response templates.", "offset": 0},
            {"owner": "manager", "title": "Shadow sessions", "desc": "Set up 3 shadowing sessions for the first 2 weeks.", "offset": 1},
        ],
        "plan": {
            "employee": {
                "day30": "Handle common tickets with supervision; learn product basics.",
                "day60": "Own a queue segment; improve macros/templates.",
                "day90": "Lead complex cases; propose CS process improvements."
            },
            "manager": {
                "day30": "Set quality bar and review loop.",
                "day60": "Calibrate performance metrics and ownership.",
                "day90": "Confirm long-term focus area and growth track."
            }
        }
    }
}

DEFAULT_TEMPLATE = "general_newgrad"

@dataclass
class GeneratedTask:
    owner: str
    title: str
    description: str
    due_date: date

def generate(role: str, grade: str, start_date: date) -> tuple[List[GeneratedTask], Dict[str, Dict[str, str]], str]:
    key = f"{role}_{grade}"
    tpl = TEMPLATES.get(key) or TEMPLATES.get(DEFAULT_TEMPLATE)
    chosen = key if key in TEMPLATES else DEFAULT_TEMPLATE

    tasks: List[GeneratedTask] = []
    for t in tpl["tasks"]:
        due = start_date + timedelta(days=int(t["offset"]))
        tasks.append(GeneratedTask(owner=t["owner"], title=t["title"], description=t["desc"], due_date=due))

    plan = tpl["plan"]
    return tasks, plan, chosen
