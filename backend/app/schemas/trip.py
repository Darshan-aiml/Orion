from pydantic import BaseModel, UUID4
from typing import List, Optional
from decimal import Decimal
import datetime

class ItineraryItemCreate(BaseModel):
    day_number: int
    component_type: str # ACTIVITY, HOTEL, GUIDE, TRANSFER
    component_id: UUID4

class TripCreate(BaseModel):
    user_id: UUID4
    name: str
    start_date: datetime.date
    end_date: datetime.date
    items: List[ItineraryItemCreate] = []

class ItineraryItemResponse(BaseModel):
    id: UUID4
    day_number: int
    component_type: str
    component_id: UUID4
    status: str

    class Config:
        from_attributes = True

class TripResponse(BaseModel):
    id: UUID4
    name: str
    total_price: Decimal
    status: str
    itinerary_items: List[ItineraryItemResponse]

    class Config:
        from_attributes = True
