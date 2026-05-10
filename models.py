from typing import TypedDict, List, Dict

class Issue(TypedDict):
    description: str
    severity: int
    confidence: float
    suggested_fix: str
    category: str

class State(TypedDict):
    task: str
    code: str

    generation: int
    max_generation: int

    security_issues: List[Issue]
    performance_issues: List[Issue]

    messages: List[Dict]