import subprocess

from pathlib import Path


def create_file(path: str, content: str) -> str:
    file_path = Path(path)

    file_path.write_text(content, encoding="utf-8")

    return f"Arquivo criado: {file_path}"

def run_command(command: str) -> str:
    print("\n--- DEBUG RUN_COMMAND ---")
    print("Comando recebido:", command)

    result = subprocess.run(
        command.split(),
        capture_output=True,
        text=True
    )

    print("Return code:", result.returncode)
    print("STDOUT:", repr(result.stdout))
    print("STDERR:", repr(result.stderr))

    output = (
        f"Return code: {result.returncode}\n"
        f"STDOUT:\n{result.stdout}\n"
        f"STDERR:\n{result.stderr}"
    )

    print("Output retornado:", repr(output))

    return output