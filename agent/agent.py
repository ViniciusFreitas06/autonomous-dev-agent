import os
import json

from pathlib import Path
from dotenv import load_dotenv
from ollama import chat
from agent import decision
from tools.tools import create_file
from agent.state import AgentState
from agent.decision import AgentDecision

load_dotenv()

ALLOWED_ACTIONS = {
    "CREATE_FILE",
}

def validate_decision(decision: AgentDecision) -> str | None:
    if decision.decision not in {"DONE", "CONTINUE"}:
        return "Decisão inválida. Use DONE ou CONTINUE."

    if decision.action != "NONE" and decision.action not in ALLOWED_ACTIONS:
        available_actions = ", ".join(ALLOWED_ACTIONS)
        return (
            f"Ação '{decision.action}' não é permitida. "
            f"Ações disponíveis: {available_actions}."
        )

    if decision.decision == "DONE" and decision.action != "NONE":
        return "Quando a decisão é DONE, a ação deve ser NONE."

    if decision.decision == "CONTINUE" and decision.action == "NONE":
        return "Quando a decisão é CONTINUE, é necessário escolher uma ação."

    return None

def validate_parameters(action: str, parameters: dict) -> str | None:
    if action == "CREATE_FILE":
        if "path" not in parameters:
            return "CREATE_FILE exige o parâmetro 'path'."

        if "content" not in parameters:
            return "CREATE_FILE exige o parâmetro 'content'."
        
        if not isinstance(parameters["path"], str):
            return "Path exige ser do tipo string."

        if not isinstance(parameters["content"], str):
            return "Content exige ser do tipo string."

    return None

def execute_action(action: str, parameters: dict) -> str:
    if action not in ALLOWED_ACTIONS:
        return f"Ação '{action}' não permitida."

    if action == "CREATE_FILE":
        path = parameters["path"]
        content = parameters["content"]
        
        return create_file(
            path,
            content
        )

    return "Ação sem implementação."

def check_goal(action: str, parameters: dict) -> bool:
    if action == "CREATE_FILE":
        path = parameters["path"]
        expected_content = parameters["content"]

        file_path = Path(path)

        if not file_path.exists():
            return False

        actual_content = file_path.read_text(encoding="utf-8")

        return actual_content == expected_content

    return False

class Agent:
    def __init__(self, goal: str):
        self.model = os.getenv("OLLAMA_MODEL")
        self.state = AgentState(goal=goal)

    def run(self, max_iterations: int = 3):
        self.state.status = "running"

        while self.state.iteration < max_iterations:
            decision = self.step()

            print(f"\nIteração {self.state.iteration}: {decision}")

            if decision.decision == "DONE" and self.state.goal_completed:
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

                    Erro da última etapa:
                    {self.state.last_error}

                    Objetivo concluído:
                    {self.state.goal_completed}

                    Use essas informações para decidir o próximo passo.

                    Se houver um erro na última etapa:
                    - analise o erro;
                    - corrija a decisão ou os parâmetros necessários;
                    - tente novamente quando fizer sentido;
                    - não considere o objetivo concluído enquanto o erro impedir a execução da tarefa.

                    Decida qual deve ser o próximo passo.

                    Você pode escolher:

                    decision:
                    - DONE: objetivo concluído
                    - CONTINUE: precisa continuar

                    action:
                    - CREATE_FILE: criar um arquivo
                    - NONE: nenhuma ação

                    parameters:
                    - Para CREATE_FILE, informe:
                    - path: caminho e nome do arquivo
                    - content: conteúdo do arquivo

                    - Para NONE, use um objeto vazio.

                    Responda SOMENTE neste formato JSON:

                    {{
                        "decision": "CONTINUE",
                        "action": "CREATE_FILE",
                        "parameters": {{
                            "path": "hello.py",
                            "content": "print('Olá mundo')"
                        }}
                    }}
                    """,
                }
            ],
        )

        print("Resposta do LLM:", response.message.content)

        decision_data = json.loads(response.message.content)

        decision = AgentDecision(
            decision=decision_data["decision"],
            action=decision_data["action"],
            parameters=decision_data["parameters"]
        )
               
        validation_error = validate_decision(decision)

        if validation_error:
            self.state.last_error = validation_error
            self.state.last_result = ""
            return decision
        
        parameter_error = validate_parameters(
            decision.action,
            decision.parameters
        )

        if parameter_error:
            self.state.last_error = parameter_error
            self.state.last_result = ""
            return decision

        self.state.last_decision = decision
        
        if decision.decision == "CONTINUE":
            try:
                result = execute_action(decision.action, decision.parameters)

                self.state.last_result = result
                self.state.last_error = ""
                self.state.goal_completed = check_goal(decision.action, decision.parameters)

            except Exception as error:
                result = f"Erro ao executar a ação: {error}"

                self.state.last_error = result
                self.state.last_result = ""
        else:
            result = "Nenhuma ferramenta executada."

        return decision