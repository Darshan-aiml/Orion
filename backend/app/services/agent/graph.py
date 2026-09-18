from langgraph.graph import StateGraph, START, END
from app.services.agent.state import AgentState
from app.services.agent.nodes import retrieve_context, search_alternatives, plan_resolution, validate_plan, commit_action

def build_agent_graph():
    """
    Constructs and compiles the LangGraph workflow for resolving trip disruptions.
    """
    workflow = StateGraph(AgentState)
    
    # Add Nodes
    workflow.add_node("retrieve_context", retrieve_context)
    workflow.add_node("search_alternatives", search_alternatives)
    workflow.add_node("plan_resolution", plan_resolution)
    workflow.add_node("validate_plan", validate_plan)
    workflow.add_node("commit_action", commit_action)
    
    # Define Edges
    workflow.add_edge(START, "retrieve_context")
    workflow.add_edge("retrieve_context", "search_alternatives")
    workflow.add_edge("search_alternatives", "plan_resolution")
    workflow.add_edge("plan_resolution", "validate_plan")
    workflow.add_edge("validate_plan", "commit_action")
    workflow.add_edge("commit_action", END)
    
    return workflow.compile()

agent_graph = build_agent_graph()
