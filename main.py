import warnings
warnings.filterwarnings("ignore")
import argparse
import sys
import os
from dotenv import load_dotenv
from utils.logger import log_experiment, ActionType
from src.tools.file_tools import list_files
from src.graph import create_refactoring_swarm_graph

load_dotenv()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target_dir", type=str, required=True)
    args = parser.parse_args()

    if not os.path.exists(args.target_dir):
        print(f"❌ Dossier {args.target_dir} introuvable.")
        sys.exit(1)

    print(f"🚀 DEMARRAGE SUR : {args.target_dir}")
    log_experiment("System", "Tool_Runner", ActionType.ANALYSIS, {"Target": args.target_dir, "input_prompt": "N/A", "output_response": "N/A"}, "INFO")

    # 1. Find all Python files in the target directory
    py_files = [f for f in list_files(args.target_dir) if not f.endswith("_test.py")]
    if not py_files:
        print(f"⚠️ Aucun fichier Python trouvé dans {args.target_dir}. Arrêt.")
        sys.exit(0)

    print(f"✅ {len(py_files)} fichiers Python trouvés. Démarrage du Swarm...")

    # 2. Initialize the LangGraph application
    app = create_refactoring_swarm_graph()
    MAX_ITERATIONS = 10 # As per the guide

    # 3. Process each file sequentially
    for file_path in py_files:
        # Resolve the test file path
        test_path = file_path.replace(".py", "_test.py")
        
        # Check if test file exists
        if not os.path.exists(test_path):
            test_path = None

        
        print(f"\n--- PROCESSING FILE: {file_path} ---")
        
        # Initial state for the graph
        initial_state = {
            "file_path": file_path,
            "test_path": test_path,
            "refactoring_plan": None,
            "test_results": None,
            "failure_report": None,
            "iteration": 0,
            "max_iterations": MAX_ITERATIONS,
            "current_file": file_path,
            "status": "START",
            "messages": []
        }

        try:
            # Run the graph with increased recursion limit
            final_state = app.invoke(initial_state, config={"recursion_limit": 50})
            
            if final_state["test_results"] and final_state["test_results"]["is_valid"]:
                print(f"✅ MISSION COMPLETE for {file_path}. Code is valid.")
            else:
                print(f"❌ MISSION FAILED for {file_path}. Code is still invalid after {final_state['iteration']} attempts.")

        except Exception as e:
            print(f"❌ CRITICAL ERROR processing {file_path}: {e}")
            log_experiment("System", "Tool_Runner", ActionType.DEBUG, {"file": file_path, "error": str(e), "input_prompt": "N/A", "output_response": "N/A"}, "FAILURE")

    print("\n✅ MISSION_COMPLETE: All files processed.")

if __name__ == "__main__":
    main()
