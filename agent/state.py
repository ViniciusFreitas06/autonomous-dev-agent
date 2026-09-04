from dataclasses import dataclass
from agent.decision import AgentDecision

@dataclass
class AgentState:
    goal: str
    status: str = "idle"
    iteration: int = 0
    last_decision: AgentDecision | None= None
    last_result: str = ""
    last_error: str = ""