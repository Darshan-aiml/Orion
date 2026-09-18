from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.trip import Trip, ItineraryItem
from app.schemas.trip import TripCreate, TripResponse
from app.services.pricing import PricingEngine
from app.services.availability import default_availability
import uuid

router = APIRouter()

@router.post("/", response_model=TripResponse)
def create_trip(trip_data: TripCreate, db: Session = Depends(get_db)):
    # 1. Create Trip record
    new_trip = Trip(
        user_id=trip_data.user_id,
        name=trip_data.name,
        start_date=trip_data.start_date,
        end_date=trip_data.end_date,
        status="DRAFT"
    )
    db.add(new_trip)
    db.flush() # To get the trip ID
    
    # 2. Add Itinerary Items and validate availability
    for item in trip_data.items:
        # Check availability
        if not default_availability.is_available(item.component_type, item.component_id, trip_data.start_date):
            db.rollback()
            raise HTTPException(status_code=400, detail=f"Component {item.component_id} is unavailable.")
            
        itinerary_item = ItineraryItem(
            trip_id=new_trip.id,
            day_number=item.day_number,
            component_type=item.component_type,
            component_id=item.component_id
        )
        db.add(itinerary_item)
    
    db.flush()
    
    # 3. Deterministically Recalculate Pricing
    PricingEngine.recalculate_trip_price(db, new_trip.id)
    
    db.commit()
    db.refresh(new_trip)
    return new_trip

@router.get("/{trip_id}", response_model=TripResponse)
def get_trip(trip_id: str, db: Session = Depends(get_db)):
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip
