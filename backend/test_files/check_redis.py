import asyncio
import redis.asyncio as redis
import os

# Default to localhost if not set
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

async def check_redis():
    print(f"Attempting to connect to Redis at: {REDIS_URL}")
    try:
        client = redis.from_url(REDIS_URL, decode_responses=True)
        # Ping
        latency = await client.ping()
        print(f"✅ Connection Successful! PING response: {latency}")
        
        # Write/Read Test
        await client.set("test_key", "Hello Redis")
        value = await client.get("test_key")
        print(f"✅ Write/Read Test Successful! Retrieved value: {value}")
        
        # Clean up
        await client.delete("test_key")
        await client.close()
        
    except Exception as e:
        print(f"❌ Redis Connection Failed: {e}")

if __name__ == "__main__":
    asyncio.run(check_redis())
