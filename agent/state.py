from dataclasses import dataclass, field

from agent.decision import AgentDecision

@dataclass
class ExpectedFile:
    path: str
    content: str

@dataclass
class ValidationSpec:
    command: str
    type: str = "command"
    expected_return_code: int = 0
    expected_stdout_contains: str | None = None

@dataclass
class AgentHistoryEntry:
    decision: str
    action: str
    parameters: dict
    result: str
    error: str


@dataclass
class AgentState:
    goal: str
    status: str = "idle"
    iteration: int = 0
    last_decision: AgentDecision | None = None
    last_result: str = ""
    last_error: str = ""
    goal_completed: bool = False
    expected_files: list[ExpectedFile] = field(default_factory=list)
    history: list[AgentHistoryEntry] = field(default_factory=list)
    validation: ValidationSpec | None = None