import os
import json

from pathlib import Path
from dotenv import load_dotenv
from ollama import chat
from agent import decision
from tools.tools import create_file, run_command
from agent.state import AgentHistoryEntry, AgentState, ExpectedFile, ValidationSpec
from agent.decision import AgentDecision

load_dotenv()

ALLOWED_ACTIONS = {
    "CREATE_FILE",
    "RUN_COMMAND",
}

ALLOWED_COMMANDS = {
    "python",
    "pytest",
}

def parse_llm_response(response_text: str):
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        return None

def record_history(
    state: AgentState,
    decision: AgentDecision,
    result: str,
    error: str
) -> None:
    history_entry = AgentHistoryEntry(
        decision=decision.decision,
        action=decision.action,
        parameters=decision.parameters,
        result=result,
        error=error
    )

    state.history.append(history_entry)

def validate_command(command: str) -> str | None:
    if not command.strip():
        return "O comando não pode ser vazio."
    
    command_name = command.split()[0]

    if command_name not in ALLOWED_COMMANDS:
        available_commands = ", ".join(ALLOWED_COMMANDS)

        return (
            f"Comando '{command_name}' não é permitido. "
            f"Comandos disponíveis: {available_commands}."
        )

    return None

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

    if action == "RUN_COMMAND":
        if "command" not in parameters:
            return "RUN_COMMAND exige o parâmetro 'command'."

        if not isinstance(parameters["command"], str):
            return "Command exige ser do tipo string."

        if not parameters["command"].strip():
            return "Command não pode ser vazio."

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

    if action == "RUN_COMMAND":
        command = parameters["command"]

        return run_command(command)

    return "Ação sem implementação."

def check_goal(state: AgentState) -> tuple[bool, str]:
    print("\n--- DEBUG VALIDAÇÃO ---")
    print("SPEC:", state.validation)

    if state.validation is None:
        print("SPEC está None")
        return False, "Nenhuma validação foi definida."

    print("Comando:", state.validation.command)
    print("Return code esperado:", state.validation.expected_return_code)
    print("STDOUT esperado:", state.validation.expected_stdout_contains)

    result = run_command(state.validation.command)

    print("Resultado da validação:")
    print(result)

    expected_return_code = state.validation.expected_return_code

    if f"Return code: {expected_return_code}" not in result:
        print("VALIDAÇÃO: FALHOU - return code")
        return (
            False,
            f"Falha: o código de retorno esperado era {expected_return_code}.\n"
            f"Resultado obtido:\n{result}"
        )

    expected_stdout = state.validation.expected_stdout_contains

    if expected_stdout:
        if expected_stdout not in result:
            print("VALIDAÇÃO: FALHOU - stdout")
            return (
                False,
                f"Falha: a saída esperada '{expected_stdout}' "
                f"não foi encontrada.\n"
                f"Resultado obtido:\n{result}"
            )

    print("VALIDAÇÃO: PASSOU")
    return True, "Validação concluída com sucesso."

class Agent:

    def __init__(self, goal: str):
        self.model = os.getenv("OLLAMA_MODEL")
        self.state = AgentState(
        goal=goal,
        validation=ValidationSpec(
        command="python hello.py",
        expected_return_code=0,
        expected_stdout_contains="hello world"
        )
    )

    def record_validation_error(
        self,
        decision: AgentDecision,
        error: str
    ) -> AgentDecision:
        self.state.last_error = error
        self.state.last_result = ""

        record_history(
            self.state,
            decision,
            "",
            error
        )

        return decision

    def run(self, max_iterations: int = 3):
        self.state.status = "running"

        while self.state.iteration < max_iterations:
            decision = self.step()

            print(f"\nIteração {self.state.iteration}: {decision}")

            if self.state.goal_completed:
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
                    - RUN_COMMAND: executar um comando permitido
                    - NONE: nenhuma ação

                    parameters:
                    - Para CREATE_FILE, informe:
                    - path: caminho e nome do arquivo
                    - content: conteúdo do arquivo

                    - Para RUN_COMMAND, informe:
                    - command: comando que deve ser executado

                    - Para NONE, use um objeto vazio.

                    - Para NONE, use um objeto vazio.

                    Responda SOMENTE neste formato JSON:

                    {{
                    "decision": "CONTINUE",
                    "action": "RUN_COMMAND",
                    "parameters": {{
                        "command": "python hello.py"
                    }}
                }}
                    """,
                }
            ],
        )

        print("Resposta do LLM:", response.message.content)

        decision_data = parse_llm_response(response.message.content)

        decision = AgentDecision(
            decision=decision_data["decision"],
            action=decision_data["action"],
            parameters=decision_data["parameters"]
        )

        self.state.last_decision = decision

        validation_error = validate_decision(decision)

        if validation_error:
            return self.record_validation_error(
                decision,
                validation_error
            )
        
        parameter_error = validate_parameters(
            decision.action,
            decision.parameters
        )

        if parameter_error:
            return self.record_validation_error(
                decision,
                parameter_error
            )

        if decision.action == "RUN_COMMAND":
            command = decision.parameters["command"]
            command_error = validate_command(command)

            if command_error:
                return self.record_validation_error(
                    decision,
                    command_error
                )
        
        if decision.decision == "CONTINUE":
            try:
                result = execute_action(decision.action, decision.parameters)

                self.state.last_result = result
                self.state.last_error = ""

                record_history(
                    self.state,
                    decision,
                    result,
                    self.state.last_error
                )

                self.state.goal_completed, validation_feedback = check_goal(self.state)
                self.state.last_result = (
                    self.state.last_result
                    + "\n\nResultado da validação:\n"
                    + validation_feedback
                )

                print("Objetivo concluído:", self.state.goal_completed)
                print("Validação:", validation_feedback)
                return decision

            except Exception as error:
                result = f"Erro ao executar a ação: {error}"
                self.state.last_error = result
                self.state.last_result = ""

        else:
            result = "Nenhuma ferramenta executada."

        record_history(
            self.state,
            decision,
            result,
            self.state.last_error
        )

        return decision