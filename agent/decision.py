from dataclasses import dataclass


@dataclass
class AgentDecision:
    decision: str
    action: str