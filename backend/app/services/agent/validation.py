import logging
from typing import Dict, Any, Tuple

logger = logging.getLogger(__name__)

def validate_agent_plan(proposed_changes: Dict[str, Any], constraints: Dict[str, Any]) -> Tuple[bool, list[str]]:
    """
    Deterministic rule engine to validate LLM proposed changes.
    Returns (is_valid, list_of_errors).
    """
    errors = []
    
    if not proposed_changes:
        return False, ["No proposed changes provided by the agent."]
        
    # Example Validation 1: Structure check
    if "replace" not in proposed_changes:
        errors.append("Proposed changes must contain a 'replace' key.")
        return False, errors
        
    # Example Validation 2: Business Rules Check
    # If the LLM proposes a new activity that exceeds the max extra cost
    if "new_cost" in proposed_changes and constraints.get("preserve_budget"):
        new_cost = proposed_changes.get("new_cost", 0)
        max_extra = constraints.get("max_extra_cost", 0)
        if new_cost > max_extra:
            errors.append(f"Proposed cost ({new_cost}) exceeds allowed extra cost ({max_extra}).")
            
    # Example Validation 3: Logical checks (e.g. replacing the same thing)
    replacement = proposed_changes.get("replace", {})
    if replacement.get("old") == replacement.get("new"):
        errors.append("Cannot replace an activity with itself.")

    is_valid = len(errors) == 0
    if not is_valid:
        logger.warning(f"Plan validation failed with errors: {errors}")
        
    return is_valid, errors
