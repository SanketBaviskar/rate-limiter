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
import json
from fastapi import HTTPException, Request, Depends
from app.redis_client import get_redis_client
from redis.asyncio import Redis

class RateLimiter:
    def __init__(self, algorithm: str = "fixed_window", limit: int = 10, window: int = 60):
        self.algorithm = algorithm
        self.limit = limit
        self.window = window

    async def check_limit(self, request: Request, redis: Redis = Depends(get_redis_client)):
        # Robust IP extraction: Always prefer X-Forwarded-For first IP
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            client_ip = forwarded.split(",")[0].strip()
        else:
            client_ip = request.client.host or "unknown"
            
        print(f"DEBUG: Rate Limiting for IP: {client_ip} (Headers: {forwarded})")
        # Allow overriding algorithm via query param for testing
        algo = request.query_params.get("algo", self.algorithm)
        
        # Dynamic Configuration Override
        try:
            config_data = await redis.get("config:rate_limit")
            if config_data:
                config = json.loads(config_data)
                # Use dynamic values if present, else fall back to defaults
                limit = int(config.get("limit", self.limit))
                window = int(config.get("window", self.window))
            else:
                limit = self.limit
                window = self.window
        except Exception:
            limit = self.limit
            window = self.window

        key = f"rate_limit:{algo}:{client_ip}"
        
        # Global Metrics
        await redis.incr("global:total_requests")
        await redis.sadd("global:active_ips", client_ip)
        
        try:
            if algo == "fixed_window":
                await self._fixed_window(redis, key, limit, window)
            elif algo == "sliding_window_log":
                await self._sliding_window_log(redis, key, limit, window)
            elif algo == "sliding_window_counter":
                await self._sliding_window_counter(redis, key, limit, window)
            elif algo == "token_bucket":
                await self._token_bucket(redis, key, limit, window)
            elif algo == "leaky_bucket":
                await self._leaky_bucket(redis, key, limit, window)
            else:
                await self._fixed_window(redis, key, limit, window)
        except HTTPException as e:
            if e.status_code == 429:
                await redis.incr("global:total_429s")
            raise e

    async def _fixed_window(self, redis: Redis, key: str, limit: int, window: int):
        """
        Fixed Window Counter:
        Increments a counter for the current window.
        """
        current_window = int(time.time() / window)
        key = f"{key}:{current_window}"
        
        count = await redis.incr(key)
        if count == 1:
            await redis.expire(key, window)
            
        if count > limit:
            raise HTTPException(status_code=429, detail="Too Many Requests (Fixed Window)")

    async def _sliding_window_log(self, redis: Redis, key: str, limit: int, window: int):
        """
        Sliding Window Log:
        Stores timestamps in a Sorted Set (ZSET).
        Removes old timestamps and counts the remaining.
        """
        now = time.time()
        window_start = now - window
        
        async with redis.pipeline(transaction=True) as pipe:
            # Remove elements older than window_start
            pipe.zremrangebyscore(key, 0, window_start)
            # Add current timestamp
            pipe.zadd(key, {str(now): now})
            # Count elements in the set
            pipe.zcard(key)
            # Set expiry for the whole key to clean up if inactive
            pipe.expire(key, window + 1)
            
            results = await pipe.execute()
            
        # results[2] is the count (zcard)
        count = results[2]
        
        if count > limit:
            raise HTTPException(status_code=429, detail="Too Many Requests (Sliding Window Log)")

    async def _sliding_window_counter(self, redis: Redis, key: str, limit: int, window: int):
        """
        Sliding Window Counter (Hybrid):
        Weighted average of previous window and current window.
        """
        now = time.time()
        
        current_window = int(now / window)
        prev_window = current_window - 1
        
        curr_key = f"{key}:{current_window}"
        prev_key = f"{key}:{prev_window}"
        
        curr_count = await redis.get(curr_key)
        prev_count = await redis.get(prev_key)
        
        curr_count = int(curr_count) if curr_count else 0
        prev_count = int(prev_count) if prev_count else 0
        
        # Calculate weighted count
        time_into_window = now % window
        weight = 1 - (time_into_window / window)
        weighted_count = curr_count + (prev_count * weight)
        
        if weighted_count >= limit:
            raise HTTPException(status_code=429, detail="Too Many Requests (Sliding Window Counter)")
             
        # Increment current window
        await redis.incr(curr_key)
        await redis.expire(curr_key, window * 2)

    async def _token_bucket(self, redis: Redis, key: str, limit: int, window: int):
        """
        Token Bucket.
        """
        now = time.time()
        capacity = limit
        refill_rate = capacity / window  # tokens per second

        data_str = await redis.get(key)

        if data_str:
            try:
                data = json.loads(data_str)
                tokens = float(data.get("tokens", capacity))
                last_refill = float(data.get("last_refill", now))
            except (ValueError, TypeError, KeyError):
                # Corrupted data -> reset bucket
                tokens = capacity
                last_refill = now
        else:
            tokens = capacity
            last_refill = now

        # Refill tokens based on elapsed time
        delta = max(0.0, now - last_refill)
        filled_tokens = min(capacity, tokens + delta * refill_rate)

        if filled_tokens >= 1.0:
            new_tokens = filled_tokens - 1.0
            new_data = json.dumps({
                "tokens": new_tokens,
                "last_refill": now,
            })
            await redis.set(key, new_data)
            # expiry: keep around for ~2 windows after last use
            await redis.expire(key, int(window * 2))
            return

        raise HTTPException(status_code=429, detail="Too Many Requests (Token Bucket)")

    async def _leaky_bucket(self, redis: Redis, key: str, limit: int, window: int):
        """
        Leaky Bucket (Queue simulation).
        """
        
        # Check current queue size
        q_len = await redis.llen(key)
        
        if q_len >= limit:
             raise HTTPException(status_code=429, detail="Too Many Requests (Leaky Bucket)")
             
        # Add to queue
        await redis.lpush(key, time.time())
        # We need to make sure this key is tracked so the background worker knows to drain it.
        # We can add the key to a "active_leaky_buckets" set.
        await redis.sadd("active_leaky_buckets", key)
