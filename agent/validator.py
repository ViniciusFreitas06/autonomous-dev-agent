from agent.state import AgentState
from tools.tools import run_command


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
