"""
main.py - FastAPI Rate Limiter Application

This is the main FastAPI application that demonstrates various rate limiting algorithms.
It includes:
- Multiple rate limiting strategies (Fixed Window, Sliding Window, Token Bucket, Leaky Bucket)
- Weather API integration with rate limiting applied
- Monitoring dashboard endpoints
- Health check endpoint for Redis connectivity
- Background worker for Leaky Bucket algorithm

Endpoints:
- GET /                          - API information
- GET /api/health                - Health check and Redis status
- GET /api/monitor               - Monitoring metrics
- GET /api/image/{w}/{h}         - Placeholder image (rate limited)
- GET /api/weather/forecast      - Weather forecast (rate limited)
- GET /api/weather/current/{id}  - Current conditions (rate limited)
"""

from fastapi import FastAPI, Depends, Response, BackgroundTasks
from app.rate_limiter import RateLimiter
from app.utils import generate_placeholder_svg
from app.redis_client import get_redis_client
from app.get_data import get_weather_data, get_current_conditions
import asyncio
import os
import json
from pydantic import BaseModel

from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Rate Limiter Project")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
            # Dynamic Config
            config_data = await redis.get("config:rate_limit")
            if config_data:
                config = json.loads(config_data)
                limit = int(config.get("limit", rate_limiter.limit))
                window = int(config.get("window", rate_limiter.window))
            else:
                limit = rate_limiter.limit
                window = rate_limiter.window
            
            leak_interval = window / limit

            # Get all active buckets
            active_buckets = await redis.smembers("active_leaky_buckets")
            
            for key in active_buckets:
                # Remove one item from the queue (leak)
                # RPOP removes and returns the last element
                await redis.rpop(key)
                
            await asyncio.sleep(leak_interval)
        except Exception as e:
            print(f"Error in leaky bucket worker: {e}")
            await asyncio.sleep(1)

class RateLimitConfig(BaseModel):
    limit: int
    window: int

@app.post("/api/config")
async def update_config(config: RateLimitConfig, redis=Depends(get_redis_client)):
    """
    Updates the rate limit configuration dynamically.
    """
    try:
        await redis.set("config:rate_limit", json.dumps(config.dict()))
        return {"status": "success", "message": f"Updated config: Limit={config.limit}, Window={config.window}s"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/reset")
async def reset_stats(redis=Depends(get_redis_client)):
    """
    Resets all rate limit counters and stats in Redis.
    """
    try:
        await redis.flushall()
        return {"status": "success", "message": "All stats and limits reset"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

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

@app.get("/api/health")
async def health_check(redis=Depends(get_redis_client)):
    """
    Health check endpoint that verifies Redis connectivity
    """
    try:
        # Test Redis connection
        await redis.ping()
        is_fakeredis = "FakeRedis" in str(type(redis))
        
        # Get some basic info
        test_key = "health_check_test"
        await redis.set(test_key, "working", ex=10)
        test_value = await redis.get(test_key)
        
        return {
            "status": "healthy",
            "redis": {
                "connected": True,
                "is_fakeredis": is_fakeredis,
                "type": str(type(redis).__name__),
                "test_write": test_value == "working"
            },
            "api": "running"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "redis": {
                "connected": False,
                "error": str(e)
            },
            "api": "running"
        }

@app.get("/")
async def root():
    return {
        "message": "Rate Limiter API is running",
        "endpoints": {
            "health": "/api/health",
            "image": "/api/image/{width}/{height}",
            "weather_forecast": "/api/weather/forecast?latitude={lat}&longitude={lon}",
            "weather_current": "/api/weather/current/{station_id}",
            "monitor": "/api/monitor"
        }
    }


