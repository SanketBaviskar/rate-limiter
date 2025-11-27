"""
rate_limiter.py - Rate Limiting Algorithms Implementation

This module implements various rate limiting strategies using Redis as the backend store.

Supported Algorithms:
1. Fixed Window Counter
   - Simple counter that resets at fixed time intervals
   - Fast but can allow bursts at window boundaries
   
2. Sliding Window Log
   - Maintains timestamps in a sorted set
   - Precise but memory-intensive for high traffic
   
3. Sliding Window Counter (Hybrid)
   - Weighted average of current and previous windows
   - Good balance between accuracy and performance
   
4. Token Bucket
   - Tokens refill at a constant rate
   - Allows controlled bursts
   
5. Leaky Bucket
   - Requests queue and leak at constant rate
   - Smooths out traffic spikes

Usage:
    rate_limiter = RateLimiter(limit=10, window=60)
    # Apply as FastAPI dependency
    @app.get("/endpoint")
    async def endpoint(request_passed: None = Depends(rate_limiter.check_limit)):
        ...
"""

import time
import asyncio
from fastapi import HTTPException, Request, Depends
from app.redis_client import get_redis_client
from redis.asyncio import Redis

class RateLimiter:
    def __init__(self, algorithm: str = "fixed_window", limit: int = 10, window: int = 60):
        self.algorithm = algorithm
        self.limit = limit
        self.window = window

    async def check_limit(self, request: Request, redis: Redis = Depends(get_redis_client)):
        client_ip = request.client.host
        # Allow overriding algorithm via query param for testing
        algo = request.query_params.get("algo", self.algorithm)
        
        key = f"rate_limit:{algo}:{client_ip}"
        
        # Global Metrics
        await redis.incr("global:total_requests")
        await redis.sadd("global:active_ips", client_ip)
        
        try:
            if algo == "fixed_window":
                await self._fixed_window(redis, key)
            elif algo == "sliding_window_log":
                await self._sliding_window_log(redis, key)
            elif algo == "sliding_window_counter":
                await self._sliding_window_counter(redis, key)
            elif algo == "token_bucket":
                await self._token_bucket(redis, key)
            elif algo == "leaky_bucket":
                await self._leaky_bucket(redis, key)
            else:
                await self._fixed_window(redis, key)
        except HTTPException as e:
            if e.status_code == 429:
                await redis.incr("global:total_429s")
            raise e

    async def _fixed_window(self, redis: Redis, key: str):
        """
        Fixed Window Counter:
        Increments a counter for the current window.
        """
        # We can use a simple key with expiration
        # However, to avoid the race condition of "check then set", we can use INCR
        # If key doesn't exist, INCR sets it to 1.
        
        # We need a key that changes every window. 
        # Or we can just set a TTL on the first write.
        
        current_count = await redis.incr(key)
        if current_count == 1:
            await redis.expire(key, self.window)
            
        if current_count > self.limit:
            raise HTTPException(status_code=429, detail="Too Many Requests (Fixed Window)")

    async def _sliding_window_log(self, redis: Redis, key: str):
        """
        Sliding Window Log:
        Stores timestamps in a Sorted Set (ZSET).
        Removes old timestamps and counts the remaining.
        """
        now = time.time()
        window_start = now - self.window
        
        async with redis.pipeline(transaction=True) as pipe:
            # Remove elements older than window_start
            pipe.zremrangebyscore(key, 0, window_start)
            # Add current timestamp
            pipe.zadd(key, {str(now): now})
            # Count elements in the set
            pipe.zcard(key)
            # Set expiry for the whole key to clean up if inactive
            pipe.expire(key, self.window + 1)
            
            results = await pipe.execute()
            
        # results[2] is the count (zcard)
        count = results[2]
        
        if count > self.limit:
            raise HTTPException(status_code=429, detail="Too Many Requests (Sliding Window Log)")

    async def _sliding_window_counter(self, redis: Redis, key: str):
        """
        Sliding Window Counter (Hybrid):
        Weighted average of previous window and current window.
        """
        now = time.time()
        window_size = self.window
        
        current_window_key = f"{key}:{int(now // window_size)}"
        previous_window_key = f"{key}:{int(now // window_size) - 1}"
        
        # Get counts
        curr_count = await redis.get(current_window_key)
        prev_count = await redis.get(previous_window_key)
        
        curr_count = int(curr_count) if curr_count else 0
        prev_count = int(prev_count) if prev_count else 0
        
        # Calculate weighted count
        time_into_window = now % window_size
        weight = 1 - (time_into_window / window_size)
        weighted_count = curr_count + (prev_count * weight)
        
        if weighted_count >= self.limit:
             raise HTTPException(status_code=429, detail="Too Many Requests (Sliding Window Counter)")
             
        # Increment current window
        await redis.incr(current_window_key)
        await redis.expire(current_window_key, window_size * 2) # Keep it around for next window calculation

    async def _token_bucket(self, redis: Redis, key: str):
        """
        Token Bucket:
        Simple non-atomic implementation for debugging.
        """
        import json
        now = time.time()
        capacity = self.limit
        refill_rate = self.limit / self.window
        
        data_str = await redis.get(key)
        if data_str:
            try:
                data = json.loads(data_str)
                tokens = float(data.get("tokens", capacity))
                last_refill = float(data.get("last_refill", now))
            except:
                tokens = capacity
                last_refill = now
        else:
            tokens = capacity
            last_refill = now
            
        delta = now - last_refill
        filled_tokens = min(capacity, tokens + (delta * refill_rate))
        
        if filled_tokens >= 1:
            new_tokens = filled_tokens - 1
            new_data = json.dumps({"tokens": new_tokens, "last_refill": now})
            await redis.set(key, new_data)
            await redis.expire(key, 60)
            return
        else:
            raise HTTPException(status_code=429, detail="Too Many Requests (Token Bucket)")

    async def _leaky_bucket(self, redis: Redis, key: str):
        """
        Leaky Bucket:
        Requests enter a queue. Queue leaks at a constant rate.
        If queue is full, reject.
        """
        
        # Check current queue size
        q_len = await redis.llen(key)
        # print(f"Leaky Bucket {key}: len={q_len}, limit={self.limit}")
        
        if q_len >= self.limit:
             raise HTTPException(status_code=429, detail="Too Many Requests (Leaky Bucket)")
             
        # Add to queue
        await redis.lpush(key, time.time())
        # We need to make sure this key is tracked so the background worker knows to drain it.
        # We can add the key to a "active_leaky_buckets" set.
        await redis.sadd("active_leaky_buckets", key)

