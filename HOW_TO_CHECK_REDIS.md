# How to Check if Redis is Installed

## Quick Answer

Run any of these commands:

### Option 1: PowerShell Script (Recommended)

```powershell
.\Check-Redis.ps1
```

This provides a comprehensive color-coded check.

### Option 2: Batch Script

```cmd
check_redis.bat
```

Simple text-based check for Windows.

### Option 3: API Health Endpoint

```powershell
curl http://localhost:8000/api/health
```

Checks if Redis is working with your FastAPI app.

### Option 4: Direct Redis Commands

```bash
# Check if redis-cli exists
redis-cli --version

# Check if Redis is running
redis-cli ping
# Should return: PONG

# Check process
Get-Process redis-server
```

---

## What Each Script Checks

All scripts verify:

1. **Redis CLI installed** - `redis-cli` command available
2. **Redis Server installed** - `redis-server` command available
3. **Redis Process Running** - Process is active in memory
4. **Port 6379 Open** - Redis default port is listening
5. **Redis Connection Works** - Can PING Redis successfully
6. **Python Package** - `redis` Python module is installed

---

## Understanding the Results

### ✅ All Checks Pass

```
[SUCCESS] Redis is installed and working!
```

**What this means:**

-   Redis server is installed and running
-   Your FastAPI app will use real Redis
-   Rate limiting data will persist
-   Multiple instances can share state

### ⚠️ Python Package Only

```
[WARNING] Redis server is NOT running!
Your app will use FakeRedis (in-memory fallback)
```

**What this means:**

-   Python package is installed but server isn't running
-   App will use FakeRedis (fallback mode)
-   Data won't persist between restarts
-   Won't work across multiple app instances

**To fix:** Start Redis server

```bash
redis-server
```

### ❌ Redis Not Installed

```
[FAIL] Redis is NOT installed!
```

**What this means:**

-   Redis is not on your system
-   App will use FakeRedis automatically

**To fix:** Install Redis (see options below)

---

## Installation Options

### Option 1: Windows Native

1. **Download Redis for Windows:**

    - https://github.com/microsoftarchive/redis/releases
    - Download `Redis-x64-3.0.504.msi` or latest

2. **Install:**

    - Run the installer
    - Keep default settings
    - Redis will start automatically

3. **Verify:**
    ```bash
    redis-cli ping
    ```

### Option 2: WSL (Windows Subsystem for Linux)

1. **Install WSL (if not installed):**

    ```powershell
    wsl --install
    ```

2. **In WSL terminal:**

    ```bash
    sudo apt update
    sudo apt install redis-server
    ```

3. **Start Redis:**

    ```bash
    sudo service redis-server start
    ```

4. **Verify:**
    ```bash
    redis-cli ping
    ```

### Option 3: Docker

1. **Install Docker Desktop**

2. **Run Redis container:**

    ```bash
    docker run -d --name redis -p 6379:6379 redis:latest
    ```

3. **Verify:**

    ```bash
    redis-cli ping
    ```

4. **Stop Redis:**

    ```bash
    docker stop redis
    ```

5. **Restart later:**
    ```bash
    docker start redis
    ```

### Option 4: Use FakeRedis (Development Only)

If you don't want to install Redis:

```powershell
# Set environment variable
$env:USE_FAKEREDIS="true"

# Restart your app
uvicorn app.main:app --reload
```

**Limitations:**

-   Data doesn't persist
-   Won't work with multiple app instances
-   Only for local development

---

## Common Issues & Solutions

### Issue: "redis-cli: command not found"

**Solution:** Redis is not in PATH

-   Reinstall Redis
-   Or add Redis install folder to system PATH
-   Or use full path: `C:\path\to\redis-cli.exe`

### Issue: "Could not connect to Redis at 127.0.0.1:6379"

**Solution:** Redis server isn't running

```bash
redis-server
```

### Issue: Port 6379 already in use

**Solution:** Another service is using the port

-   Find what's using it: `netstat -ano | findstr 6379`
-   Stop that service or use different port

### Issue: Python ImportError: No module named redis

**Solution:** Install Python package

```bash
pip install redis fakeredis
```

---

## Monitoring Redis

### View all keys

```bash
redis-cli KEYS "*"
```

### Monitor commands in real-time

```bash
redis-cli MONITOR
```

### Get server info

```bash
redis-cli INFO
```

### Check rate limiting keys

```bash
# List all rate limit keys
redis-cli KEYS "ratelimit:*"

# Get total requests
redis-cli GET "global:total_requests"

# Get total 429s (rate limit hits)
redis-cli GET "global:total_429s"
```

---

## Quick Reference

| Command                    | Purpose                                   |
| -------------------------- | ----------------------------------------- |
| `redis-server`             | Start Redis server                        |
| `redis-cli ping`           | Test connection                           |
| `redis-cli --version`      | Check version                             |
| `Get-Process redis-server` | Check if running (PowerShell)             |
| `redis-cli KEYS "*"`       | List all keys                             |
| `redis-cli INFO`           | Server information                        |
| `redis-cli FLUSHALL`       | **Clear all data** (⚠️ Use with caution!) |

---

## Your Current Status

Based on the health check at `/api/health`:

```json
{
	"status": "healthy",
	"redis": {
		"connected": true,
		"is_fakeredis": false,
		"type": "Redis"
	}
}
```

**Your Redis IS installed and working! ✅**

-   Real Redis is running
-   Not using FakeRedis fallback
-   Ready for production use
