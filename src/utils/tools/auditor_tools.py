from .file_tools import read_file
from .analysis_tools import run_pylint

def get_code_for_audit(file_path: str) -> str:
    code = read_file(file_path)
    analysis = run_pylint(file_path)
    return f"--- SOURCE CODE ---\n{code}\n\n--- PYLINT ANALYSIS ---\n{analysis['report']}"
