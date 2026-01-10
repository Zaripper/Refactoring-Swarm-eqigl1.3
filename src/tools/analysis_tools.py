import subprocess

def run_pylint(file_path: str) -> dict:
    try:
        result = subprocess.run(['pylint', '--output-format=text', file_path], capture_output=True, text=True)
        return {"report": result.stdout, "status": "SUCCESS"}
    except Exception as e: return {"report": str(e), "status": "FAILURE"}

def run_pytest(test_path: str) -> dict:
    try:
        result = subprocess.run(['pytest', '-v', test_path], capture_output=True, text=True)
        return {"stdout": result.stdout, "stderr": result.stderr, "exit_code": result.returncode, "status": "SUCCESS" if result.returncode == 0 else "FAILED"}
    except Exception as e: return {"error": str(e), "status": "ERROR"}
