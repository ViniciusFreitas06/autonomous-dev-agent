
import os
import json

from dotenv import load_dotenv
from ollama import chat

load_dotenv()


class Planner:

    def __init__(self):
        self.model = os.getenv("OLLAMA_MODEL")

    def create_plan(self, goal: str) -> dict:

        response = chat(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": f"""
                    Você é um planejador de tarefas para um agente
                    autônomo de desenvolvimento de software.

                    Seu trabalho é transformar o objetivo em etapas
                    pequenas, claras e executáveis.

                    Objetivo:
                    {goal}

                    Responda SOMENTE com JSON válido neste formato:

                    {{
                        "goal": "objetivo resumido",
                        "steps": [
                            "primeira etapa",
                            "segunda etapa"
                        ]
                    }}

                    Não execute nenhuma ação.
                    Apenas crie o plano.
                    """
                }
            ],
        )

        plan = json.loads(response.message.content)

        return plan