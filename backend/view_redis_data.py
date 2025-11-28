"""
view_redis_data.py - Redis Data Viewer

This script displays all data stored in Redis by the rate limiter application.
It shows keys, values, types, and TTLs in a readable format.

Usage: py view_redis_data.py
"""

import asyncio
import redis.asyncio as redis
import os
import json
from datetime import datetime, timedelta

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

def format_timestamp(ts):
    """Convert Unix timestamp to readable datetime"""
    try:
        return datetime.fromtimestamp(float(ts)).strftime('%Y-%m-%d %H:%M:%S')
    except:
        return str(ts)

async def view_redis_store():
    """Connect to Redis and display all stored data"""
    
    print("\n" + "="*70)
    print("  REDIS DATA STORE VIEWER")
    print("="*70)
    
    try:
        # Connect to Redis
        client = redis.from_url(REDIS_URL, decode_responses=True)
        await client.ping()
        print(f"\n✓ Connected to Redis at {REDIS_URL}\n")
        
        # Get all keys
        all_keys = await client.keys("*")
        
        if not all_keys:
            print("⚠  Redis is empty - no keys found")
            await client.close()
            return
        
        print(f"Found {len(all_keys)} keys\n")
        print("-"*70)
        
        # Organize keys by category
        categories = {
            "Global Metrics": [],
            "Fixed Window": [],
            "Sliding Window Log": [],
            "Sliding Window Counter": [],
            "Token Bucket": [],
            "Leaky Bucket": [],
            "Active Buckets": [],
            "Other": []
        }
        
        for key in sorted(all_keys):
            if key.startswith("global:"):
                categories["Global Metrics"].append(key)
            elif "fixed_window" in key:
                categories["Fixed Window"].append(key)
            elif "sliding_window_log" in key:
                categories["Sliding Window Log"].append(key)
            elif "sliding_window_counter" in key:
                categories["Sliding Window Counter"].append(key)
            elif "token_bucket" in key:
                categories["Token Bucket"].append(key)
            elif "leaky_bucket" in key.lower():
                categories["Leaky Bucket"].append(key)
            elif "active_leaky_buckets" in key:
                categories["Active Buckets"].append(key)
            else:
                categories["Other"].append(key)
        
        # Display each category
        for category, keys in categories.items():
            if not keys:
                continue
                
            print(f"\n📊 {category}")
            print("-"*70)
            
            for key in keys:
                key_type = await client.type(key)
                ttl = await client.ttl(key)
                
                # Format TTL
                if ttl == -1:
                    ttl_str = "No expiration"
                elif ttl == -2:
                    ttl_str = "Key expired"
                else:
                    ttl_str = f"{ttl}s ({timedelta(seconds=ttl)})"
                
                print(f"\n  Key: {key}")
                print(f"  Type: {key_type}")
                print(f"  TTL: {ttl_str}")
                
                # Get value based on type
                try:
                    if key_type == "string":
                        value = await client.get(key)
                        # Try to parse as JSON
                        try:
                            parsed = json.loads(value)
                            print(f"  Value: {json.dumps(parsed, indent=10)}")
                        except:
                            print(f"  Value: {value}")
                            
                    elif key_type == "zset":  # Sorted set (Sliding Window Log)
                        members = await client.zrange(key, 0, -1, withscores=True)
                        print(f"  Count: {len(members)}")
                        if members:
                            print(f"  Timestamps:")
                            for member, score in members[:10]:  # Show first 10
                                print(f"    - {format_timestamp(score)} ({score})")
                            if len(members) > 10:
                                print(f"    ... and {len(members) - 10} more")
                                
                    elif key_type == "list":  # Leaky Bucket queue
                        length = await client.llen(key)
                        items = await client.lrange(key, 0, 9)  # First 10 items
                        print(f"  Queue Length: {length}")
                        if items:
                            print(f"  Items (newest first):")
                            for item in items:
                                print(f"    - {format_timestamp(item)}")
                            if length > 10:
                                print(f"    ... and {length - 10} more")
                                
                    elif key_type == "set":  # Active IPs or buckets
                        members = await client.smembers(key)
                        print(f"  Members ({len(members)}):")
                        for member in sorted(members):
                            print(f"    - {member}")
                            
                    elif key_type == "hash":
                        hash_data = await client.hgetall(key)
                        print(f"  Fields:")
                        for field, value in hash_data.items():
                            print(f"    {field}: {value}")
                            
                except Exception as e:
                    print(f"  Error reading value: {e}")
        
        # Summary
        print("\n" + "="*70)
        print("  SUMMARY")
        print("="*70)
        
        # Get global stats if they exist
        total_requests = await client.get("global:total_requests")
        total_429s = await client.get("global:total_429s")
        active_ips = await client.smembers("global:active_ips")
        
        print(f"\nTotal Requests: {total_requests or 0}")
        print(f"Total 429 Responses: {total_429s or 0}")
        print(f"Active IPs: {len(active_ips) if active_ips else 0}")
        if active_ips:
            print(f"  {', '.join(sorted(active_ips))}")
        
        print(f"\nTotal Keys: {len(all_keys)}")
        
        # Get Redis info
        info = await client.info("memory")
        print(f"Memory Used: {info.get('used_memory_human', 'N/A')}")
        
        print("\n" + "="*70 + "\n")
        
        await client.close()
        
    except redis.ConnectionError:
        print("\n❌ Cannot connect to Redis!")
        print(f"   Make sure Redis is running on {REDIS_URL}\n")
    except Exception as e:
        print(f"\n❌ Error: {e}\n")

if __name__ == "__main__":
    asyncio.run(view_redis_store())
