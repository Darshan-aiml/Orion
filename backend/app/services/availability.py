from abc import ABC, abstractmethod
import uuid
import datetime

class AvailabilityProvider(ABC):
    @abstractmethod
    def check_availability(self, component_type: str, component_id: uuid.UUID, date: datetime.date) -> bool:
        pass

class RealAvailabilityProvider(AvailabilityProvider):
    def check_availability(self, component_type: str, component_id: uuid.UUID, date: datetime.date) -> bool:
        # In the future, this would integrate with actual APIs (Amadeus, Viator, etc.)
        raise NotImplementedError("Real integration not yet configured.")

class MockAvailabilityProvider(AvailabilityProvider):
    def check_availability(self, component_type: str, component_id: uuid.UUID, date: datetime.date) -> bool:
        # Deterministic mock logic: for the MVP, let's say ID starting with 'f' is unavailable
        # or we can just randomly/deterministically return True.
        # We will return True by default, but allow specific scenarios to fail.
        
        # Simple deterministic mock:
        return True

class AvailabilityService:
    def __init__(self, provider: AvailabilityProvider):
        self.provider = provider
        
    def is_available(self, component_type: str, component_id: uuid.UUID, date: datetime.date) -> bool:
        return self.provider.check_availability(component_type, component_id, date)

# Default to mock for MVP
default_availability = AvailabilityService(MockAvailabilityProvider())
