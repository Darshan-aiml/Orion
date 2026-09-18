import uuid
from sqlalchemy import Column, String, Numeric, Integer, ForeignKey, DateTime, Date, Time
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base

class Trip(Base):
    __tablename__ = 'trips'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    name = Column(String(255), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    total_price = Column(Numeric(10, 2), nullable=False, default=0.00)
    status = Column(String(50), nullable=False, default="DRAFT") # DRAFT, CONFIRMED, CANCELLED, ACTIVE
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    itinerary_items = relationship("ItineraryItem", back_populates="trip", cascade="all, delete-orphan")

class ItineraryItem(Base):
    __tablename__ = 'itinerary_items'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trip_id = Column(UUID(as_uuid=True), ForeignKey('trips.id'), nullable=False)
    day_number = Column(Integer, nullable=False)
    start_time = Column(Time, nullable=True)
    end_time = Column(Time, nullable=True)
    
    component_type = Column(String(50), nullable=False) # ACTIVITY, HOTEL, GUIDE, TRANSFER
    component_id = Column(UUID(as_uuid=True), nullable=False) # Reference to Activity, Guide etc.
    
    status = Column(String(50), nullable=False, default="PLANNED") # PLANNED, COMPLETED, DISRUPTED, REPLACED
    agent_constraints = Column(JSONB, default=dict) # {"replacement_allowed": True, "preserve_budget": True}
    
    trip = relationship("Trip", back_populates="itinerary_items")
