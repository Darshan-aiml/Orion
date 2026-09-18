import logging
from app.core.celery_app import celery_app
from app.services.agent.graph import agent_graph

logger = logging.getLogger(__name__)

@celery_app.task(name="app.tasks.run_agent_workflow")
def run_agent_workflow(event_data: dict):
    """
    Executes the LangGraph agent workflow asynchronously to handle an event.
    """
    logger.info(f"Starting agent workflow for event: {event_data.get('event_id')}")
    
    initial_state = {
        "event_id": event_data.get("event_id", "unknown"),
        "event_type": event_data.get("event_type", "unknown"),
        "payload": event_data.get("payload", {})
    }
    
    final_state = agent_graph.invoke(initial_state)
    
    logger.info(f"Successfully processed agent workflow. Proposed reasoning: {final_state.get('reasoning_summary')}")
    return {"status": "success", "event_id": final_state["event_id"]}
