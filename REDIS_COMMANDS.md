# Redis Store Viewer - Quick Commands

## Open Redis CLI

redis-cli

## Once in Redis CLI:

# 1. View ALL keys

KEYS \*

# 2. View rate limiting keys only

KEYS ratelimit:\*

# 3. View specific algorithm keys

KEYS ratelimit:fixed_window:_
KEYS ratelimit:sliding_window_log:_
KEYS ratelimit:token_bucket:_
KEYS leaky_bucket:_

# 4. View global metrics

GET global:total_requests
GET global:total_429s
SMEMBERS global:active_ips

# 5. Get details about a specific key

TYPE ratelimit:fixed_window:127.0.0.1
GET ratelimit:fixed_window:127.0.0.1
TTL ratelimit:fixed_window:127.0.0.1

# 6. View sliding window log (sorted set)

ZRANGE ratelimit:sliding_window_log:127.0.0.1 0 -1 WITHSCORES

# 7. View leaky bucket queue

LRANGE leaky_bucket:127.0.0.1 0 -1

# 8. Monitor Redis commands in real-time

MONITOR

# 9. Get Redis server info

INFO
INFO stats

# 10. Count total keys

DBSIZE

# Exit Redis CLI

EXIT
