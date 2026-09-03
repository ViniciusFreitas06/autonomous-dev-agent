from dataclasses import dataclass


@dataclass
class AgentState:
    goal: str
    status: str = "idle"
    iteration: int = 0
    last_decision: str = ""
    last_result: str = ""