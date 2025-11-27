import redis.asyncio as redis
import os
import fakeredis.aioredis

# Use environment variable for Redis URL or default to localhost
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
USE_FAKEREDIS = os.getenv("USE_FAKEREDIS", "False").lower() == "true"

# Create a Redis client instance
# We will initialize it lazily or just handle the connection error
redis_client = None
fake_server = None

async def get_redis_client():
    """
    Dependency to get the Redis client.
    Falls back to fakeredis if real Redis is not available.
    """
    global redis_client, fake_server
    
    if redis_client is None:
        if USE_FAKEREDIS:
            print("Using FakeRedis...")
            if fake_server is None:
                fake_server = fakeredis.FakeServer()
            redis_client = fakeredis.aioredis.FakeRedis(server=fake_server, decode_responses=True)
        else:
            try:
                # Try to create a real client
                client = redis.from_url(REDIS_URL, decode_responses=True)
                # Test connection
                await client.ping()
                redis_client = client
                print(f"Connected to Redis at {REDIS_URL}")
            except Exception as e:
                print(f"Could not connect to Redis: {e}")
                print("Falling back to FakeRedis...")
                if fake_server is None:
                    fake_server = fakeredis.FakeServer()
                redis_client = fakeredis.aioredis.FakeRedis(server=fake_server, decode_responses=True)
    
    return redis_client
