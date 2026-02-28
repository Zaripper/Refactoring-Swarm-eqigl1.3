import os
from typing import TypedDict, List, Optional
from dotenv import load_dotenv, find_dotenv


from langchain_core.messages import HumanMessage, SystemMessage

from src.analysis_tools import run_pylint
from src.file_tools import read_file, write_file
from src.judge_tools import run_pytest
from src.logger import log_experiment, ActionType

load_dotenv(find_dotenv())

# --- 2. INITIALIZE GEMINI ---
from langchain_google_genai import ChatGoogleGenerativeAI
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0,
    convert_system_message_to_human=True
)

# --- 3. DEFINE STATE ---
class AgentState(TypedDict):
    file_path: str
    test_path: str
    refactoring_plan: Optional[List[str]]
    test_results: Optional[dict]
    failure_report: Optional[str]
    iteration: int
    max_iterations: int
    current_file: Optional[str]
    status: Optional[str]
    messages: Optional[List[str]]

# --- 4. AUDITOR AGENT ---
def auditor_agent(state: AgentState):
    file_path = state["file_path"]
    print(f"🔍 Auditor: Analyzing {file_path}...")
    
    code = read_file(file_path)
    lint = run_pylint(file_path)
    
    prompt = f"""
    Analyze this code and pylint report. 
    Return a concise refactoring plan as a bulleted list.
    CODE:
    {code}
    REPORT:
    {lint}
    """
    
    response = llm.invoke([
        SystemMessage(content="You are a Code Auditor."), 
        HumanMessage(content=prompt)
    ])
    
    plan = response.content.split("\n")
    
    # LOGGING FIX
    details = {
        "file": file_path,
        "input_prompt": prompt,
        "output_response": response.content
    }
    
    log_experiment("Auditor", "gemini-2.5-flash", file_path, ActionType.ANALYSIS, details, "SUCCESS")
    
    return {"refactoring_plan": plan, "iteration": state["iteration"] + 1, "current_file": file_path, "status": "SUCCESS"}

# --- 5. FIXER AGENT ---
def fixer_agent(state: AgentState):
    file_path = state["file_path"]
    plan_text = "\n".join(state["refactoring_plan"]) if state["refactoring_plan"] else "Fix all errors."
    code = read_file(file_path)
    
    print(f"🔧 Fixer: Fixing {file_path}...")
    
    prompt = f"""
    Apply this plan to the code. Output ONLY python code.
    PLAN:
    {plan_text}
    CODE:
    {code}
    """
    
    response = llm.invoke([
        SystemMessage(content="You are a Fixer. Output only code. No markdown."), 
        HumanMessage(content=prompt)
    ])
    
    clean_code = response.content.replace("```python", "").replace("```", "").strip()
    write_file(file_path, clean_code)
    
    # LOGGING FIX
    details = {
        "file": file_path,
        "input_prompt": prompt,
        "output_response": clean_code
    }
    
    log_experiment("Fixer", "gemini-2.5-flash", file_path, ActionType.FIX, details, "SUCCESS")
    
    return {"failure_report": None, "status": "SUCCESS"}

# --- 6. JUDGE AGENT ---
def judge_tool_runner(state: AgentState):
    print("⚖️ Judge: Testing...")
    test_path = state["test_path"]
    
    if test_path and os.path.exists(test_path):
        report = run_pytest(test_path)
        is_success = report.get("exit_code", 1) == 0
        status_str = "SUCCESS" if is_success else "FAILURE"
    else:
        report = {"status": "SKIPPED", "message": "No test file found"}
        is_success = True
        status_str = "SUCCESS"

    log_experiment("Judge", "Tool", state["file_path"], ActionType.DEBUG, {"report": report, "input_prompt": "Running tests", "output_response": str(report)}, status_str)
    
    return {
        "test_results": {"is_valid": is_success, "output": report},
        "failure_report": report if not is_success else None,
        "status": status_str
    }

# --- 7. ROUTER ---
def decide_next_step(state: AgentState):
    if state["test_results"] and state["test_results"].get("is_valid"):
        print("✅ SUCCESS: Code fixed.")
        return "END"
    
    if state["iteration"] >= state["max_iterations"]:
        print("⚠️ FAIL: Max retries.")
        return "END"
    
    print("↺ LOOP: Retrying...")
    return "FIX"
