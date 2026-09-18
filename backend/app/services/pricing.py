from decimal import Decimal
from typing import List
import uuid

from sqlalchemy.orm import Session
from app.models.trip import Trip, ItineraryItem
from app.models.inventory import Activity, Guide

class PricingEngine:
    """
    Deterministic pricing engine for trips. 
    The AI Agent must NEVER determine prices; it must use this service.
    """
    
    TAX_RATE = Decimal('0.10') # 10% tax
    SERVICE_FEE = Decimal('0.05') # 5% platform fee
    
    @classmethod
    def calculate_itinerary_cost(cls, session: Session, itinerary_items: List[ItineraryItem]) -> Decimal:
        base_cost = Decimal('0.00')
        
        for item in itinerary_items:
            # Depending on component type, query the base price
            if item.component_type == "ATTRACTION" or item.component_type == "ACTIVITY":
                activity = session.query(Activity).filter_by(id=item.component_id).first()
                if activity:
                    base_cost += activity.base_price
            elif item.component_type == "GUIDE":
                guide = session.query(Guide).filter_by(id=item.component_id).first()
                if guide:
                    # In a real app, this would multiply by duration, for MVP assume 1 day rate
                    base_cost += guide.base_price_per_day
                    
            # HOTEL and TRANSFER would go here...
            
        return base_cost

    @classmethod
    def recalculate_trip_price(cls, session: Session, trip_id: uuid.UUID) -> Decimal:
        trip = session.query(Trip).filter_by(id=trip_id).first()
        if not trip:
            raise ValueError("Trip not found")
            
        base_cost = cls.calculate_itinerary_cost(session, trip.itinerary_items)
        
        markup = base_cost * cls.SERVICE_FEE
        taxes = (base_cost + markup) * cls.TAX_RATE
        
        final_price = base_cost + markup + taxes
        
        # Update trip price
        trip.total_price = final_price
        session.add(trip)
        session.commit()
        
        return final_price
