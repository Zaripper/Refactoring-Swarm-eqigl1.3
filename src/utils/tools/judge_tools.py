from .analysis_tools import run_pytest, run_pylint

def validate_code(test_path: str, file_path: str) -> dict:
    test_results = run_pytest(test_path)
    quality_results = run_pylint(file_path)
    return {"tests": test_results, "quality": quality_results, "is_valid": test_results["status"] == "SUCCESS"}
