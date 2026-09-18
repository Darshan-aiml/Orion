from pydantic import BaseModel, UUID4
from typing import List, Optional
from decimal import Decimal

class DestinationResponse(BaseModel):
    id: UUID4
    name: str
    country: str
    description: Optional[str]

    class Config:
        from_attributes = True

class GuideResponse(BaseModel):
    id: UUID4
    name: str
    bio: Optional[str]
    languages: List[str]
    specializations: List[str]
    base_price_per_day: Decimal
    rating: Optional[float]

    class Config:
        from_attributes = True

class ActivityResponse(BaseModel):
    id: UUID4
    name: str
    activity_type: str
    description: Optional[str]
    base_price: Decimal
    duration_mins: Optional[int]

    class Config:
        from_attributes = True
