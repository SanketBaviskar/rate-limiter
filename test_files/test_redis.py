"""
Redis Connection Test Script
Tests if Redis is running and accessible
"""
import asyncio
import redis.asyncio as redis
import os

async def test_redis_connection():
    """Test Redis connection"""
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    print("="*60)
    print("Redis Connection Test")
    print("="*60)
    print(f"\nTesting connection to: {redis_url}\n")
    
    try:
        # Create Redis client
        client = redis.from_url(redis_url, decode_responses=True)
        
        # Test 1: PING
        print("Test 1: PING command...")
        response = await client.ping()
        print(f"✅ PING response: {response}")
        
        # Test 2: SET and GET
        print("\nTest 2: SET/GET commands...")
        await client.set("test_key", "Hello Redis!")
        value = await client.get("test_key")
        print(f"✅ SET/GET successful: {value}")
        
        # Test 3: DELETE
        print("\nTest 3: DELETE command...")
        await client.delete("test_key")
        value = await client.get("test_key")
        print(f"✅ DELETE successful: {value is None}")
        
        # Test 4: Check Redis info
        print("\nTest 4: Getting Redis server info...")
        info = await client.info("server")
        print(f"✅ Redis version: {info.get('redis_version', 'N/A')}")
        print(f"✅ OS: {info.get('os', 'N/A')}")
        print(f"✅ Uptime (seconds): {info.get('uptime_in_seconds', 'N/A')}")
        
        # Test 5: Check memory usage
        print("\nTest 5: Memory usage...")
        memory_info = await client.info("memory")
        used_memory = memory_info.get('used_memory_human', 'N/A')
        print(f"✅ Memory used: {used_memory}")
        
        await client.close()
        
        print("\n" + "="*60)
        print("✅ All tests passed! Redis is working properly.")
        print("="*60)
        
        return True
        
    except redis.ConnectionError as e:
        print(f"\n❌ Connection Error: {e}")
        print("\nPossible solutions:")
        print("1. Make sure Redis is installed")
        print("2. Start Redis server: redis-server")
        print("3. Check if Redis is running on port 6379")
        print("4. Check firewall settings")
        return False
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_redis_connection())
    exit(0 if result else 1)
