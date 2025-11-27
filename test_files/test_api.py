import asyncio
import aiohttp
import time
import sys
import redis.asyncio as redis
from redis.asyncio import Redis

BASE_URL = "http://localhost:8000/api/image/200/200"
LIMIT = 10
WINDOW = 60

async def wait_for_server():
    """Wait for the local FastAPI server to be up."""
    health_url = "http://localhost:8000/api/health"
    print("Waiting for server to be ready...")
    async with aiohttp.ClientSession() as session:
        for i in range(10):
            try:
                async with session.get(health_url) as resp:
                    if resp.status == 200:
                        print("Server is ready!")
                        return
            except Exception:
                await asyncio.sleep(1)
                print(".", end="", flush=True)
    print("\nServer not reachable on http://localhost:8000/")
    sys.exit(1)

async def clear_redis():
    """Clears all keys in the local Redis instance."""
    try:
        r = redis.from_url("redis://localhost:6379/0")
        await r.flushall()
        await r.close()
        # print("[INFO] Redis cleared.")
    except Exception as e:
        print(f"[WARN] Could not clear Redis: {e}")

async def fetch(session, algo, i):
    """Sends a single async request."""
    start = time.time()
    try:
        async with session.get(f"{BASE_URL}?algo={algo}") as response:
            status = response.status
            # Read body to ensure request completes
            await response.read() 
            end = time.time()
            return i, status, start, end
    except Exception as e:
        return i, f"Error: {e}", start, time.time()

import datetime

async def test_1rps(algo, total_requests=20):
    """
    Sends requests at 1 request per second.
    """
    print(f"\n=== 1 Request Per Second Test for: {algo} ===")
    print(f"Sending {total_requests} requests (1 per second)...")
    
    await clear_redis()
    
    async with aiohttp.ClientSession() as session:
        print("-" * 65)
        print(f"{'Req':<5} | {'Time':<12} | {'Status':<10} | {'Duration (s)':<10}")
        print("-" * 65)
        
        success_count = 0
        blocked_count = 0
        
        for i in range(1, total_requests + 1):
            start = time.time()
            try:
                async with session.get(f"{BASE_URL}?algo={algo}") as response:
                    status = response.status
                    await response.read()
                    end = time.time()
                    
                    duration = end - start
                    now_str = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
                    
                    if status == 200:
                        success_count += 1
                        status_str = "✅ 200"
                    elif status == 429:
                        blocked_count += 1
                        status_str = "⛔ 429"
                    else:
                        status_str = f"⚠️ {status}"
                        
                    print(f"{i:<5} | {now_str:<12} | {status_str:<10} | {duration:<10.3f}")
                    
            except Exception as e:
                print(f"{i:<5} | Error: {e}")
            
            # Wait for the remainder of the second
            elapsed = time.time() - start
            sleep_time = max(0, 1.0 - elapsed)
            await asyncio.sleep(sleep_time)
            
        print("-" * 65)
        print(f"Results: Success={success_count}, Blocked={blocked_count}")

async def test_burst_concurrent(algo, total_requests=20):
    """
    Sends 'total_requests' concurrently (with tiny delay) to test burst.
    """
    print(f"\n=== Concurrent Burst Test for: {algo} ===")
    print(f"Sending {total_requests} requests (burst)...")
    
    await clear_redis()
    
    async with aiohttp.ClientSession() as session:
        tasks = []
        start_global = time.time()
        
        # Create tasks with 0.05s delay
        for i in range(1, total_requests + 1):
            tasks.append(asyncio.create_task(fetch(session, algo, i)))
            await asyncio.sleep(0.05)
            
        results = await asyncio.gather(*tasks)
        
        # Sort by Request ID
        results.sort(key=lambda x: x[0])
        
        success_count = 0
        blocked_count = 0
        
        print("-" * 65)
        print(f"{'Req':<5} | {'Time':<12} | {'Status':<10} | {'Duration (s)':<10}")
        print("-" * 65)
        
        # We need to reconstruct the "Time" roughly from start time
        # But better to just print the start time relative to global start
        # Or capture real time in fetch? fetch captures start time.
        # Let's convert start time to string.
        
        for i, status, start, end in results:
            duration = end - start
            start_dt = datetime.datetime.fromtimestamp(start).strftime("%H:%M:%S.%f")[:-3]
            
            if status == 200:
                success_count += 1
                status_str = "✅ 200"
            elif status == 429:
                blocked_count += 1
                status_str = "⛔ 429"
            else:
                status_str = f"⚠️ {status}"
                
            print(f"{i:<5} | {start_dt:<12} | {status_str:<10} | {duration:<10.3f}")

        print("-" * 65)
        print(f"Results: Success={success_count}, Blocked={blocked_count}")
        
        if success_count > LIMIT:
             # Allow +1 for Token Bucket due to refill during test (1.2s test duration allows ~0.2 tokens)
             # If it's 11, it's acceptable for Token Bucket.
            if algo == "token_bucket" and success_count <= LIMIT + 1:
                 print(f"✅ SUCCESS: Allowed {success_count} requests (Acceptable for Token Bucket refill).")
            else:
                 print(f"❌ FAILURE: Allowed {success_count} requests (Limit is {LIMIT}).")
        else:
            print(f"✅ SUCCESS: Allowed {success_count} requests.")

async def main():
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
    await wait_for_server()
    
    algorithms = [
        "fixed_window", 
        "sliding_window_log", 
        "sliding_window_counter", 
        "token_bucket", 
        "leaky_bucket"
    ]
    
    for algo in algorithms:
        print(f"\n{'='*70}")
        print(f"TESTING ALGORITHM: {algo}")
        print(f"{'='*70}")
        
        # 1. Test 1 Request Per Second
        await test_1rps(algo, total_requests=15)
        
        # Small pause
        await asyncio.sleep(1)
        
        # 2. Test Burst
        await test_burst_concurrent(algo, total_requests=20)
        
        print("\n\n")

if __name__ == "__main__":
    asyncio.run(main())
