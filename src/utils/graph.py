# src/graph.py
from langgraph.graph import StateGraph, END
from src.agents import AgentState, auditor_agent, fixer_agent, judge_tool_runner, decide_next_step

def create_refactoring_swarm_graph():
    """
    Creates and compiles the LangGraph workflow for the Refactoring Swarm.
    """
    # 1. Define the graph state
    workflow = StateGraph(AgentState)

    # 2. Add the nodes (agents)
    workflow.add_node("auditor", auditor_agent)
    workflow.add_node("fixer", fixer_agent)
    workflow.add_node("judge", judge_tool_runner)

    # 3. Set the entry point
    workflow.set_entry_point("auditor")

    # 4. Define the edges (transitions)
    
    # Auditor always goes to Fixer after creating the plan
    workflow.add_edge("auditor", "fixer")
    
    # Fixer always goes to Judge after applying the fix
    workflow.add_edge("fixer", "judge")
    
    # Judge decides the next step: FIX (loop) or END (success/max iterations)
    workflow.add_conditional_edges(
        "judge",
        decide_next_step,
        {
            "FIX": "fixer", # Loop back to the fixer
            "END": END      # Mission complete for this file
        }
    )

    # 5. Compile the graph
    app = workflow.compile()
    return app
