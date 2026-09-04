from pathlib import Path


def create_file(path: str, content: str) -> str:
    file_path = Path(path)

    file_path.write_text(content, encoding="utf-8")

    return f"Arquivo criado: {file_path}"

