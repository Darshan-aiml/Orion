import logging
import json
import asyncio
import redis.asyncio as aioredis
from app.core.config import settings

logger = logging.getLogger(__name__)

CHANNEL_PREFIX = "agent:trip:"

async def get_redis() -> aioredis.Redis:
    return await aioredis.from_url(settings.REDIS_URL, decode_responses=True)

async def publish_agent_event(trip_id: str, event: dict):
    """
    Publishes an agent event to a Redis PubSub channel for a specific trip.
    Called by the Celery action engine after a plan is committed.
    """
    r = await get_redis()
    channel = f"{CHANNEL_PREFIX}{trip_id}"
    await r.publish(channel, json.dumps(event))
    await r.aclose()
    logger.info(f"Published agent event to channel: {channel}")

async def subscribe_to_trip(trip_id: str):
    """
    Async generator that subscribes to a trip's Redis channel and
    yields Server-Sent Event formatted messages.
    """
    r = await get_redis()
    pubsub = r.pubsub()
    channel = f"{CHANNEL_PREFIX}{trip_id}"
    await pubsub.subscribe(channel)
    logger.info(f"SSE client subscribed to: {channel}")

    try:
        # Send initial connection confirmation
        yield f"data: {json.dumps({'type': 'connected', 'trip_id': trip_id})}\n\n"

        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=30)
            if message and message["type"] == "message":
                yield f"data: {message['data']}\n\n"
            else:
                # Heartbeat to keep the connection alive
                yield f": heartbeat\n\n"
            await asyncio.sleep(0.5)
    except asyncio.CancelledError:
        logger.info(f"SSE client disconnected from: {channel}")
    finally:
        await pubsub.unsubscribe(channel)
        await r.aclose()
