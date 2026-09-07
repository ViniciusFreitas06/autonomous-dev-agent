import subprocess

from pathlib import Path


def create_file(path: str, content: str) -> str:
    file_path = Path(path)

    file_path.write_text(content, encoding="utf-8")

    return f"Arquivo criado: {file_path}"

def run_command(command: str) -> str:
    result = subprocess.run(
        command,
        capture_output=True,
        text=True
    )

    return (
        f"Return code: {result.returncode}\n"
        f"STDOUT:\n{result.stdout}\n"
        f"STDERR:\n{result.stderr}"
    )
