from fastapi import APIRouter

router = APIRouter()

from .discovery import router as discovery_router
from .trips import router as trips_router

router.include_router(discovery_router, prefix="/discovery", tags=["Discovery"])
router.include_router(trips_router, prefix="/trips", tags=["Trips"])
