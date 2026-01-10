from .file_tools import write_file

def apply_refactoring(file_path: str, content: str) -> str:
    return write_file(file_path, content)
