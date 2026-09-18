from typing import TypedDict, Optional, List, Dict, Any

class AgentState(TypedDict):
    """
    Represents the state of the trip disruption resolution workflow.
    """
    # Initial Event Details
    event_id: str
    event_type: str
    payload: Dict[str, Any]
    
    # Context Retrieval
    trip_id: Optional[str]
    current_itinerary: Optional[List[Dict[str, Any]]]
    constraints: Optional[Dict[str, Any]]
    
    # Semantic Search
    search_results: Optional[List[Dict[str, Any]]]
    
    # Planning
    proposed_changes: Optional[Dict[str, Any]]
    reasoning_summary: Optional[str]
    
    # Validation & Finalization
    validation_result: Optional[Dict[str, Any]]
    status: str
