# Project Structure

## Core Application Files

### `app/main.py`

**Purpose:** Main FastAPI application entry point

-   Defines all API endpoints
-   Sets up rate limiting middleware
-   Manages background workers for Leaky Bucket algorithm
-   Includes CORS configuration
-   Serves static files

**Key Endpoints:**

-   `GET /` - API information
-   `GET /api/health` - Health check and Redis status
-   `GET /api/monitor` - Monitoring metrics
-   `GET /api/image/{w}/{h}` - Placeholder image (rate limited)
-   `GET /api/weather/forecast` - Weather forecast (rate limited)
-   `GET /api/weather/current/{id}` - Current conditions (rate limited)

---

### `app/rate_limiter.py`

**Purpose:** Rate limiting algorithms implementation

-   Implements 5 different rate limiting strategies
-   Uses Redis for distributed state management
-   Can be applied as FastAPI dependency

**Algorithms Implemented:**

1. **Fixed Window Counter** - Simple counter with fixed reset intervals
2. **Sliding Window Log** - Precise timestamp-based tracking
3. **Sliding Window Counter** - Hybrid approach with weighted averaging
4. **Token Bucket** - Allows controlled bursts with token refills
5. **Leaky Bucket** - Queue-based smoothing of traffic spikes

---

### `app/redis_client.py`

**Purpose:** Redis connection manager

-   Handles Redis connection initialization
-   Automatic fallback to FakeRedis if real Redis unavailable
-   Lazy connection initialization
-   Environment variable configuration support

---

### `app/get_data.py`

**Purpose:** Weather API integration

-   Fetches data from National Weather Service API
-   Async functions for FastAPI compatibility
-   Proper error handling and response formatting

**Functions:**

-   `get_weather_data(lat, lon)` - 7-day forecast
-   `get_current_conditions(station_id)` - Current weather

---

### `app/utils.py`

**Purpose:** Utility functions

-   Helper functions used across the application
-   Currently includes SVG placeholder generator

---

## Configuration Files

### `requirements.txt`

**Purpose:** Python dependencies

```
fastapi
uvicorn[standard]
redis
httpx
```

### `Dockerfile`

**Purpose:** Docker container configuration

-   Defines how to build the application container
-   Used with docker-compose for deployment

---

## Testing & Diagnostic Tools

### `Check-Redis.ps1`

**Purpose:** PowerShell script to check Redis installation

-   Comprehensive color-coded checks
-   Tests Redis CLI, server, process, port, connection
-   Checks Python package and API health
-   Provides installation instructions if needed

**Usage:** `.\Check-Redis.ps1`

---

### `check_redis.bat`

**Purpose:** Batch file to check Redis installation

-   Windows CMD version of Redis checker
-   Same checks as PowerShell version
-   Text-based output

**Usage:** `check_redis.bat`

---

### `test_files/` Directory

**Purpose:** Contains test scripts (moved to keep project organized)

-   `test_api.py` - API endpoint tests
-   `test_weather_api.py` - Weather API integration tests
-   `test_redis.py` - Redis connection tests
-   `check_redis_installation.py` - Python-based Redis checker

---

## Documentation

### `README.md`

**Purpose:** Main project documentation

-   Project overview
-   Quick start guide
-   API endpoint documentation
-   Rate limiting configuration
-   Docker setup instructions

---

### `HOW_TO_CHECK_REDIS.md`

**Purpose:** Redis installation and verification guide

-   Multiple methods to check Redis status
-   Installation instructions for different platforms
-   Troubleshooting common issues
-   Monitoring and debugging commands

---

## Frontend Files

### `static/index.html`

**Purpose:** Monitoring dashboard

-   Static HTML/CSS/JS dashboard
-   Visualizes rate limiting metrics
-   Real-time monitoring of API requests

### `frontend/` Directory

**Purpose:** React-based frontend (optional enhanced UI)

-   More advanced monitoring interface
-   Uses Vite for development
-   Tailwind CSS for styling

---

## Git Files

### `.gitignore`

**Purpose:** Git ignore rules

-   Excludes temporary files
-   Ignores Python cache directories
-   Excludes node_modules and build artifacts
-   Keeps repository clean

---

## Project Organization

```
Rate Limiter/
├── app/                    # Core application code
│   ├── main.py            # FastAPI app
│   ├── rate_limiter.py    # Rate limiting logic
│   ├── redis_client.py    # Redis connection
│   ├── get_data.py        # Weather API
│   └── utils.py           # Utilities
│
├── static/                # Static files
│   └── index.html         # Dashboard
│
├── frontend/              # React frontend (optional)
│
├── test_files/            # Test scripts
│
├── Check-Redis.ps1        # Redis checker (PowerShell)
├── check_redis.bat        # Redis checker (Batch)
│
├── requirements.txt       # Python dependencies
├── Dockerfile             # Docker config
├── README.md              # Main documentation
├── HOW_TO_CHECK_REDIS.md  # Redis guide
└── .gitignore             # Git ignore rules
```

---

## Quick Reference

| File                    | Purpose             | When to Use                       |
| ----------------------- | ------------------- | --------------------------------- |
| `app/main.py`           | Run the API         | `uvicorn app.main:app --reload`   |
| `Check-Redis.ps1`       | Check Redis         | Before running the app            |
| `requirements.txt`      | Install deps        | `pip install -r requirements.txt` |
| `README.md`             | Learn about project | First time setup                  |
| `HOW_TO_CHECK_REDIS.md` | Redis help          | Troubleshooting Redis             |

---

## All Files Have Header Comments

Every Python and script file now includes:

-   **Purpose** - What the file does
-   **Key functions/features** - Main components
-   **Usage examples** - How to use it

This makes the codebase self-documenting and easier to understand!
