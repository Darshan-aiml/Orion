import uuid
from sqlalchemy import Column, String, Text, Numeric, Integer, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from app.models.base import Base

class Destination(Base):
    __tablename__ = 'destinations'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    country = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    embedding = Column(Vector(1536), nullable=True) # OpenAI ada-002 dimension size
    
    # Relationships
    activities = relationship("Activity", back_populates="destination")
    guides = relationship("Guide", back_populates="destination")

class Activity(Base):
    __tablename__ = 'activities'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    destination_id = Column(UUID(as_uuid=True), ForeignKey('destinations.id'), nullable=False)
    name = Column(String(255), nullable=False)
    activity_type = Column(String(50), nullable=False) # ATTRACTION, RESTAURANT, TRANSFER
    description = Column(Text, nullable=True)
    base_price = Column(Numeric(10, 2), nullable=False, default=0.00)
    duration_mins = Column(Integer, nullable=True)
    opening_hours = Column(JSONB, default=dict)
    location_lat = Column(Numeric(9, 6), nullable=True)
    location_lng = Column(Numeric(9, 6), nullable=True)
    embedding = Column(Vector(1536), nullable=True)
    
    destination = relationship("Destination", back_populates="activities")

class Guide(Base):
    __tablename__ = 'guides'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), unique=True, nullable=True)
    destination_id = Column(UUID(as_uuid=True), ForeignKey('destinations.id'), nullable=False)
    name = Column(String(255), nullable=False)
    bio = Column(Text, nullable=True)
    languages = Column(JSONB, default=list) # e.g. ["en", "fr"]
    specializations = Column(JSONB, default=list) # e.g. ["Heritage", "Food"]
    base_price_per_day = Column(Numeric(10, 2), nullable=False, default=0.00)
    rating = Column(Numeric(3, 2), nullable=True)
    embedding = Column(Vector(1536), nullable=True)
    
    destination = relationship("Destination", back_populates="guides")
