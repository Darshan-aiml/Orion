from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.services.sse.redis_pubsub import subscribe_to_trip

router = APIRouter()

@router.get("/trip/{trip_id}")
async def trip_event_stream(trip_id: str):
    """
    Server-Sent Events endpoint. Connect here to receive live agent updates
    for a specific trip via Redis PubSub.
    
    Usage: EventSource('/api/v1/stream/trip/{trip_id}')
    """
    return StreamingResponse(
        subscribe_to_trip(trip_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # Disables Nginx buffering for SSE
            "Connection": "keep-alive",
        },
    )
