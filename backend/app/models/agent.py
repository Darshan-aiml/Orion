import uuid
from sqlalchemy import Column, String, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from app.models.base import Base

class AgentEvent(Base):
    """External events that trigger the AI agent (e.g., Attraction Closed)"""
    __tablename__ = 'agent_events'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_type = Column(String(100), nullable=False) # e.g., ATTRACTION_CLOSED, WEATHER_WARNING
    payload = Column(JSONB, nullable=False) # Details about the event
    status = Column(String(50), nullable=False, default="PENDING") # PENDING, PROCESSED, FAILED
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class AgentAction(Base):
    """Audit log of what the agent proposed and what was actually applied"""
    __tablename__ = 'agent_actions'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id = Column(UUID(as_uuid=True), ForeignKey('agent_events.id'), nullable=False)
    trip_id = Column(UUID(as_uuid=True), ForeignKey('trips.id'), nullable=False)
    
    reasoning_summary = Column(String(500), nullable=True) # User-facing explanation
    proposed_changes = Column(JSONB, nullable=False) # The diff to the itinerary
    validation_result = Column(JSONB, nullable=True) # Result from the deterministic Validation Layer
    
    status = Column(String(50), nullable=False, default="PROPOSED") # PROPOSED, VALIDATED, APPLIED, REJECTED
    created_at = Column(DateTime(timezone=True), server_default=func.now())
