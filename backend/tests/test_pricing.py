import pytest
import uuid
from decimal import Decimal
from app.services.pricing import PricingEngine
from app.models.trip import Trip, ItineraryItem
from app.models.inventory import Activity, Destination

from app.models.user import User

def test_pricing_engine(db_session):
    # Setup test data
    u = User(email=f"test_{uuid.uuid4()}@example.com")
    db_session.add(u)
    db_session.flush()

    d = Destination(name="Test", country="Test")
    db_session.add(d)
    db_session.flush()
    
    a = Activity(destination_id=d.id, name="Test Activity", activity_type="ATTRACTION", base_price=100.00)
    db_session.add(a)
    db_session.flush()
    
    trip = Trip(user_id=u.id, name="Test Trip", start_date="2024-01-01", end_date="2024-01-05")
    db_session.add(trip)
    db_session.flush()
    
    item = ItineraryItem(trip_id=trip.id, day_number=1, component_type="ATTRACTION", component_id=a.id)
    db_session.add(item)
    db_session.commit()
    
    # Calculate price
    final_price = PricingEngine.recalculate_trip_price(db_session, trip.id)
    
    # Base = 100.00
    # Markup = 5% = 5.00
    # Subtotal = 105.00
    # Tax = 10% = 10.50
    # Total = 115.50
    assert final_price == Decimal('115.50')
