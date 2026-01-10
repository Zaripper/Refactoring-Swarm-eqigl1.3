import os
SANDBOX_DIR = os.path.abspath("sandbox")

def is_within_sandbox(file_path: str) -> bool:
    abs_path = os.path.abspath(file_path)
    return abs_path.startswith(SANDBOX_DIR)

def read_file(file_path: str) -> str:
    if not os.path.exists(file_path): return f"Error: File {file_path} not found."
    with open(file_path, 'r', encoding='utf-8') as f: return f.read()

def write_file(file_path: str, content: str) -> str:
    if not is_within_sandbox(file_path): return f"Error: Security Violation."
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f: f.write(content)
    return f"Success: File written to {file_path}"

def list_files(directory: str) -> list:
    if not os.path.exists(directory): return []
    return [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.py')]
