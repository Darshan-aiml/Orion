from fastapi import APIRouter

router = APIRouter()

from .discovery import router as discovery_router
from .trips import router as trips_router
from .events import router as events_router
from .stream import router as stream_router

router.include_router(discovery_router, prefix="/discovery", tags=["Discovery"])
router.include_router(trips_router, prefix="/trips", tags=["Trips"])
router.include_router(events_router, prefix="/events", tags=["Events"])
router.include_router(stream_router, prefix="/stream", tags=["Stream"])
