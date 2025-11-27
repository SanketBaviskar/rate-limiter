# How to View Redis Store Data

There are several ways to inspect what's stored in your Redis database:

---

## 🎯 Quick Methods

### Method 1: PowerShell Script (Easiest)

```powershell
.\View-RedisData.ps1
```

**Shows:** All keys organized by category with types, values, and TTLs

### Method 2: Python Script

```bash
py view_redis_data.py
```

**Shows:** Detailed formatted output with timestamps and statistics

### Method 3: Via API

```bash
curl http://localhost:8000/api/monitor
```

**Shows:** Global metrics (total requests, 429s, active IPs)

---

## 🔧 Using Redis CLI

### Basic Commands

**1. Open Redis CLI:**

```bash
redis-cli
```

**2. View all keys:**

```bash
127.0.0.1:6379> KEYS *
```

**3. View specific patterns:**

```bash
# Rate limiting keys
KEYS ratelimit:*

# Fixed window keys
KEYS ratelimit:fixed_window:*

# Sliding window log keys
KEYS ratelimit:sliding_window_log:*

# Token bucket keys
KEYS ratelimit:token_bucket:*

# Leaky bucket keys
KEYS leaky_bucket:*

# Global metrics
KEYS global:*
```

**4. Get a specific value:**

```bash
# String value (Fixed Window counter)
GET ratelimit:fixed_window:127.0.0.1

# Check TTL (time to live)
TTL ratelimit:fixed_window:127.0.0.1
```

**5. View sorted set (Sliding Window Log):**

```bash
# Count items
ZCARD ratelimit:sliding_window_log:127.0.0.1

# View all items with scores (timestamps)
ZRANGE ratelimit:sliding_window_log:127.0.0.1 0 -1 WITHSCORES

# View recent 10 items
ZRANGE ratelimit:sliding_window_log:127.0.0.1 -10 -1 WITHSCORES
```

**6. View list (Leaky Bucket queue):**

```bash
# Get queue length
LLEN leaky_bucket:127.0.0.1

# View queue items
LRANGE leaky_bucket:127.0.0.1 0 -1
```

**7. View set members (Active IPs):**

```bash
SMEMBERS global:active_ips
```

**8. View global counters:**

```bash
GET global:total_requests
GET global:total_429s
SCARD global:active_ips
```

---

## 📊 Understanding Key Patterns

Your rate limiter uses these key patterns:

### Global Metrics

-   `global:total_requests` - Total API requests count
-   `global:total_429s` - Total rate limit hits
-   `global:active_ips` - Set of active IP addresses

### Fixed Window

-   `ratelimit:fixed_window:{ip}` - Counter (integer)
-   **Type:** String
-   **Value:** Request count in current window
-   **TTL:** Expires at end of window (60s default)

### Sliding Window Log

-   `ratelimit:sliding_window_log:{ip}` - Timestamps
-   **Type:** Sorted Set (ZSET)
-   **Value:** Timestamp as both member and score
-   **TTL:** Window duration + 1 second

### Sliding Window Counter

-   `ratelimit:sliding_window_counter:{ip}:{window_id}` - Counter
-   **Type:** String
-   **Value:** Request count for that window
-   **TTL:** 2x window duration

### Token Bucket

-   `ratelimit:token_bucket:{ip}` - State object
-   **Type:** String (JSON)
-   **Value:** `{"tokens": 9.5, "last_refill": 1234567890}`
-   **TTL:** 60 seconds

### Leaky Bucket

-   `leaky_bucket:{ip}` - Request queue
-   **Type:** List
-   **Value:** Timestamps of requests in queue
-   **TTL:** None (cleaned by worker)
-   `active_leaky_buckets` - Set of active bucket keys

---

## 🔍 Monitoring in Real-Time

### Watch Redis Commands

```bash
redis-cli MONITOR
```

This shows every command executed against Redis in real-time.

### Auto-refresh Keys

```powershell
# PowerShell - refresh every 2 seconds
while ($true) {
    Clear-Host
    redis-cli KEYS "*"
    Start-Sleep 2
}
```

### Watch Specific Metric

```powershell
# Watch total requests counter
while ($true) {
    Clear-Host
    Write-Host "Total Requests: $(redis-cli GET global:total_requests)"
    Write-Host "Total 429s: $(redis-cli GET global:total_429s)"
    Start-Sleep 1
}
```

---

## 🧪 Testing & Inspecting

### 1. Make some requests to generate data

```bash
# Make requests to trigger rate limiting
for ($i=1; $i -le 15; $i++) {
    curl "http://localhost:8000/api/weather/forecast?latitude=39&longitude=-94"
}
```

### 2. View the Redis data

```powershell
.\View-RedisData.ps1
```

### 3. Or use Redis CLI

```bash
redis-cli

# See what was created
KEYS *

# Check your IP's fixed window counter
GET ratelimit:fixed_window:127.0.0.1

# Check global metrics
GET global:total_requests
GET global:total_429s
```

---

## 📈 Key Information Commands

### Database Statistics

```bash
redis-cli INFO stats
redis-cli INFO memory
redis-cli DBSIZE  # Total number of keys
```

### Memory Usage

```bash
redis-cli INFO memory | findstr used_memory_human
```

### Key Details

```bash
# Check type of a key
redis-cli TYPE ratelimit:fixed_window:127.0.0.1

# Check size
redis-cli STRLEN ratelimit:fixed_window:127.0.0.1  # For strings
redis-cli LLEN leaky_bucket:127.0.0.1  # For lists
redis-cli ZCARD ratelimit:sliding_window_log:127.0.0.1  # For sorted sets

# Memory used by a key
redis-cli MEMORY USAGE ratelimit:fixed_window:127.0.0.1
```

---

## 🧹 Clearing Data

### Clear specific keys

```bash
redis-cli DEL ratelimit:fixed_window:127.0.0.1
```

### Clear by pattern

```bash
redis-cli KEYS "ratelimit:*" | ForEach-Object { redis-cli DEL $_ }
```

### Clear ALL data (⚠️ USE WITH CAUTION!)

```bash
redis-cli FLUSHALL
```

---

## 💡 Quick Examples

### Example 1: Check your current rate limit status

```bash
# For your IP address (usually 127.0.0.1 locally)
redis-cli GET ratelimit:fixed_window:127.0.0.1
redis-cli TTL ratelimit:fixed_window:127.0.0.1
```

### Example 2: See which IPs are currently active

```bash
redis-cli SMEMBERS global:active_ips
```

### Example 3: Count how many rate limit hits

```bash
redis-cli GET global:total_429s
```

### Example 4: View sliding window timestamps

```bash
redis-cli ZRANGE ratelimit:sliding_window_log:127.0.0.1 0 -1 WITHSCORES
```

---

## 🎨 GUI Tools (Optional)

If you prefer a graphical interface:

1. **Redis Insight** (Official)

    - Download: https://redis.io/insight/
    - Connect to localhost:6379
    - Visual key browser and value editor

2. **RedisDesktopManager**

    - https://resp.app/
    - Cross-platform GUI

3. **Medis** (Mac)
    - https://getmedis.com/

---

## 🔗 Additional Resources

-   **Redis CLI Reference:** https://redis.io/docs/manual/cli/
-   **Redis Commands:** https://redis.io/commands/
-   **Data Types:** https://redis.io/docs/data-types/

---

## Summary Commands

| What to View         | Command                                          |
| -------------------- | ------------------------------------------------ |
| All keys             | `redis-cli KEYS "*"`                             |
| Your rate limit      | `redis-cli GET ratelimit:fixed_window:127.0.0.1` |
| Total requests       | `redis-cli GET global:total_requests`            |
| Active IPs           | `redis-cli SMEMBERS global:active_ips`           |
| Monitor live         | `redis-cli MONITOR`                              |
| Database size        | `redis-cli DBSIZE`                               |
| Everything formatted | `.\View-RedisData.ps1`                           |
