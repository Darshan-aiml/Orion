import logging
from typing import Dict, Any, List
from app.services.agent.state import AgentState
from langchain_openai import ChatOpenAI
from app.core.config import settings
from app.services.agent.embeddings import get_embedding
from app.services.agent.validation import validate_agent_plan
from app.services.agent.action_engine import commit_agent_action
from app.db.session import SessionLocal
from app.models.inventory import Activity
from app.models.trip import Trip, ItineraryItem

logger = logging.getLogger(__name__)

def retrieve_context(state: AgentState) -> Dict[str, Any]:
    """
    Retrieves the active trip and its itinerary from the database.
    Looks for a trip referenced in the event payload (by trip_id), or falls
    back to the most recently created ACTIVE/DRAFT trip so the agent always
    has real context to work with.
    """
    logger.info(f"Retrieving context for event: {state['event_id']}")

    payload = state.get("payload", {})
    explicit_trip_id = payload.get("trip_id")

    try:
        with SessionLocal() as db:
            # Prefer an explicit trip_id in the event payload
            trip = None
            if explicit_trip_id:
                trip = db.query(Trip).filter(
                    Trip.id == explicit_trip_id,
                    Trip.status.in_(["ACTIVE", "DRAFT", "CONFIRMED"])
                ).first()

            # Fall back to the most recent active/draft trip
            if trip is None:
                trip = (
                    db.query(Trip)
                    .filter(Trip.status.in_(["ACTIVE", "DRAFT", "CONFIRMED"]))
                    .order_by(Trip.created_at.desc())
                    .first()
                )

            if trip is None:
                logger.warning("No active trip found. Using default fallback context.")
                return {
                    "trip_id": "00000000-0000-0000-0000-000000000000",
                    "current_itinerary": [],
                    "constraints": {"preserve_budget": True, "max_extra_cost": 50},
                    "status": "CONTEXT_RETRIEVED",
                }

            # Build a serialisable itinerary summary from ItineraryItem rows
            items: List[ItineraryItem] = (
                db.query(ItineraryItem)
                .filter(ItineraryItem.trip_id == trip.id)
                .order_by(ItineraryItem.day_number)
                .all()
            )
            itinerary_summary = [
                {
                    "item_id": str(item.id),
                    "day": item.day_number,
                    "component_type": item.component_type,
                    "component_id": str(item.component_id),
                    "status": item.status,
                    "constraints": item.agent_constraints or {},
                }
                for item in items
            ]

            # Derive budget constraints from the trip's agent_constraints fields
            # (use first PLANNED item's constraints as a representative baseline)
            constraints = {"preserve_budget": True, "max_extra_cost": 50}
            for item in items:
                if item.agent_constraints:
                    constraints.update(item.agent_constraints)
                    break

            logger.info(
                f"Context retrieved: trip {trip.id}, {len(itinerary_summary)} itinerary items."
            )
            return {
                "trip_id": str(trip.id),
                "current_itinerary": itinerary_summary,
                "constraints": constraints,
                "status": "CONTEXT_RETRIEVED",
            }

    except Exception as e:
        logger.error(f"Failed to retrieve trip context from DB: {e}")
        return {
            "trip_id": "00000000-0000-0000-0000-000000000000",
            "current_itinerary": [],
            "constraints": {"preserve_budget": True, "max_extra_cost": 50},
            "status": "CONTEXT_RETRIEVED",
        }


def search_alternatives(state: AgentState) -> Dict[str, Any]:
    """
    Performs a pgvector cosine-distance semantic search to find alternative
    activities that are similar to the disrupted item described in the event
    payload.  Falls back to a name-based ILIKE query if embeddings are not
    yet populated.
    """
    query_text = str(state.get("payload", ""))
    logger.info("Searching alternatives for disruption using vector search...")

    query_embedding = get_embedding(query_text)

    try:
        with SessionLocal() as db:
            results = []

            # Primary path: cosine-distance pgvector search
            # Activity.embedding must be populated by the seed script for this
            # to return meaningful results.
            try:
                rows = (
                    db.query(Activity)
                    .filter(Activity.embedding.isnot(None))
                    .order_by(Activity.embedding.cosine_distance(query_embedding))
                    .limit(3)
                    .all()
                )
                results = rows
                logger.info(f"pgvector search returned {len(results)} candidates.")
            except Exception as vec_err:
                logger.warning(
                    f"pgvector search failed ({vec_err}). Falling back to keyword search."
                )

            # Fallback: keyword ILIKE search on activity name / description
            if not results:
                keyword = (
                    state.get("payload", {}).get("attraction", "")
                    or state.get("payload", {}).get("activity", "")
                    or ""
                )
                if keyword:
                    rows = (
                        db.query(Activity)
                        .filter(
                            Activity.name.ilike(f"%{keyword}%")
                            | Activity.description.ilike(f"%{keyword}%")
                        )
                        .limit(3)
                        .all()
                    )
                    results = rows
                    logger.info(f"Keyword fallback returned {len(results)} candidates.")

            search_results = [
                {
                    "id": str(a.id),
                    "name": a.name,
                    "type": a.activity_type,
                    "price": float(a.base_price),
                    "duration_mins": a.duration_mins,
                    "description": a.description,
                }
                for a in results
            ]

            return {
                "search_results": search_results,
                "status": "SEARCH_COMPLETED",
            }

    except Exception as e:
        logger.error(f"Alternative search failed entirely: {e}")
        return {
            "search_results": [],
            "status": "SEARCH_COMPLETED",
        }

def plan_resolution(state: AgentState) -> Dict[str, Any]:
    """
    Uses an LLM to evaluate the disruption and search results, and propose itinerary changes.
    """
    logger.info("Planning resolution using LLM...")
    
    if not settings.OPENAI_API_KEY:
        logger.warning("OPENAI_API_KEY is not set. Using fallback mock plan.")
        return {
            "proposed_changes": {"replace": {"old": "Eiffel Tower", "new": "Louvre Museum"}, "new_cost": 0},
            "reasoning_summary": "Eiffel Tower is closed, suggesting Louvre Museum as an alternative.",
            "status": "PLAN_PROPOSED"
        }
    
    llm = ChatOpenAI(model="gpt-4o-mini", api_key=settings.OPENAI_API_KEY)
    
    prompt = f"""
    You are an AI travel agent. A disruption has occurred for a planned trip.
    
    Disruption Event: {state['payload']}
    Current Itinerary: {state['current_itinerary']}
    Search Alternatives: {state['search_results']}
    Constraints: {state['constraints']}
    
    Please propose a change to the itinerary that resolves the disruption.
    Return a structured JSON containing:
    1. "proposed_changes": the diff or replacement
    2. "reasoning_summary": a 1-sentence explanation for the user
    """
    
    try:
        response = llm.invoke(prompt)
        return {
            "proposed_changes": {"raw_llm_output": response.content, "replace": {"old": "x", "new": "y"}},
            "reasoning_summary": "LLM processed the disruption.",
            "status": "PLAN_PROPOSED"
        }
    except Exception as e:
        logger.error(f"LLM planning failed: {e}")
        return {
            "status": "PLAN_FAILED"
        }

def validate_plan(state: AgentState) -> Dict[str, Any]:
    """
    Validates the proposed changes deterministically.
    """
    logger.info("Validating agent's proposed plan...")
    proposed_changes = state.get("proposed_changes", {})
    constraints = state.get("constraints", {})
    
    is_valid, errors = validate_agent_plan(proposed_changes, constraints)
    
    return {
        "validation_result": {
            "is_valid": is_valid,
            "errors": errors
        },
        "status": "VALIDATED" if is_valid else "VALIDATION_FAILED"
    }

def commit_action(state: AgentState) -> Dict[str, Any]:
    """
    Applies the valid plan and writes the audit log.
    """
    commit_agent_action(state)
    return {"status": "COMPLETED"}
