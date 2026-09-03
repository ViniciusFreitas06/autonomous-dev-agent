import os

from dotenv import load_dotenv
from ollama import chat
from tools.tools import create_file
from agent.state import AgentState
from agent.decision import AgentDecision

load_dotenv()

def execute_action(action: str) -> str:
    if action == "CREATE_FILE":
        return create_file(
            "agent_test.txt",
            "Arquivo criado pelo agente."
        )

    return "Ação desconhecida."

class Agent:
    def __init__(self, goal: str):
        self.model = os.getenv("OLLAMA_MODEL")
        self.state = AgentState(goal=goal)

    def run(self, max_iterations: int = 3):
        self.state.status = "running"

        while self.state.iteration < max_iterations:
            decision = self.step()

            print(f"\nIteração {self.state.iteration}: {decision}")

            if decision.decision == "DONE":
                self.state.status = "completed"
                break

        else:
            self.state.status = "max_iterations"    

    def step(self) -> AgentDecision:
        self.state.iteration += 1

        response = chat(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": f"""
                    Você é um agente executando uma tarefa.

                    Objetivo:
                    {self.state.goal}
                    
                    Resultado da última etapa:
                    {self.state.last_result}

                    Decida se o objetivo já foi concluído.

                    Responda SOMENTE com uma destas opções:
                    DONE
                    CONTINUE
                    """,
                }
            ],
        )
        
        decision_text = response.message.content.strip()
        decision = AgentDecision(decision=decision_text, action="CREATE_FILE" if decision_text == "CONTINUE" else "")

        self.state.last_decision = decision
        
        if decision.decision == "CONTINUE":
            result = execute_action(decision.action)
        else:
            result = "Nenhuma ferramenta executada."
        
        self.state.last_result = result

        return decision