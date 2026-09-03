import os

from dotenv import load_dotenv
from ollama import chat

from agent.state import AgentState


load_dotenv()


class Agent:
    def __init__(self, goal: str):
        self.model = os.getenv("OLLAMA_MODEL")
        self.state = AgentState(goal=goal)

    def run(self, max_iterations: int = 3):
        self.state.status = "running"

        while self.state.iteration < max_iterations:
            decision = self.step()

            print(f"\nIteração {self.state.iteration}: {decision}")

            if decision == "DONE":
                self.state.status = "completed"
                break

        else:
            self.state.status = "max_iterations"    

    def step(self) -> str:
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

                    Decida se o objetivo já foi concluído.

                    Responda SOMENTE com uma destas opções:
                    DONE
                    CONTINUE
                    """,
                }
            ],
        )
        
        decision = response.message.content.strip()
        self.state.last_decision = decision
        
        result = f"Etapa {self.state.iteration} executada."
        self.stat.last_result = result

        return decision