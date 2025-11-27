from fastapi import FastAPI, Depends, Response, BackgroundTasks
from app.rate_limiter import RateLimiter
from app.utils import generate_placeholder_svg
from app.redis_client import get_redis_client
import asyncio
import os

from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Rate Limiter Project")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize Rate Limiter
# Default: 10 requests per 60 seconds
rate_limiter = RateLimiter(limit=10, window=60)

@app.on_event("startup")
async def startup_event():
    # Start the Leaky Bucket worker
    asyncio.create_task(leaky_bucket_worker())

async def leaky_bucket_worker():
    """
    Background task to leak requests from the Leaky Bucket queues.
    Leaks 1 request every (window / limit) seconds.
    """
    redis = await get_redis_client()
    leak_interval = rate_limiter.window / rate_limiter.limit
    
    while True:
        try:
            # Get all active buckets
            active_buckets = await redis.smembers("active_leaky_buckets")
            
            for key in active_buckets:
                # Remove one item from the queue (leak)
                # RPOP removes and returns the last element
                await redis.rpop(key)
                
                # Optional: If empty, remove from active set to save cycles
                # But for now, we keep it simple.
                
            await asyncio.sleep(leak_interval)
        except Exception as e:
            print(f"Error in leaky bucket worker: {e}")
            await asyncio.sleep(1)

@app.get("/api/monitor")
async def get_monitor_data(redis=Depends(get_redis_client)):
    """
    Returns telemetry data for the dashboard.
    """
    total_requests = await redis.get("global:total_requests") or 0
    total_429s = await redis.get("global:total_429s") or 0
    active_ips = await redis.smembers("global:active_ips") or []
    
    # Gather algorithm specific data (mocked or real if we track it per algo globally)
    # For this demo, we can just return the global stats and maybe some current state for the requesting IP if we knew it.
    # But the dashboard is a separate client.
    
    # Let's return what we have.
    return {
        "globalMetrics": {
            "totalRequests": int(total_requests),
            "total429s": int(total_429s),
            "activeIPs": len(active_ips)
        },
        "algorithmData": {
            "fixed_window": {"limit": 10, "window": 60},
            "sliding_window_log": {"limit": 10, "window": 60},
            "sliding_window_counter": {"limit": 10, "window": 60},
            "token_bucket": {"limit": 10, "window": 60},
            "leaky_bucket": {"limit": 10, "window": 60}
        }
    }

@app.get("/api/image/{width}/{height}")
async def get_image(
    width: int, 
    height: int, 
    request_passed: None = Depends(rate_limiter.check_limit)
):
    """
    Returns a placeholder SVG image.
    Rate limiting is applied via the dependency.
    """
    svg_content = generate_placeholder_svg(width, height)
    return Response(content=svg_content, media_type="image/svg+xml")

@app.get("/")
async def root():
    return {"message": "Rate Limiter API is running. Go to /api/image/{width}/{height}"}
