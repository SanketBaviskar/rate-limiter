@echo off
REM ============================================================
REM check_redis.bat - Redis Installation Checker for Windows
REM
REM This batch script checks if Redis is installed and running.
REM It performs the following checks:
REM   - Redis CLI availability
REM   - Redis Server availability
REM   - Redis process running status
REM   - Port 6379 listening
REM   - Redis connection via PING
REM   - Python redis package
REM   - Environment variables
REM   - API health endpoint
REM
REM Usage: check_redis.bat
REM ============================================================
echo.
echo ============================================================
echo   Redis Installation Check
echo ============================================================
echo.

echo [1/7] Checking if redis-cli is installed...
where redis-cli >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] redis-cli found
    redis-cli --version
) else (
    echo [FAIL] redis-cli not found in PATH
)

echo.
echo [2/7] Checking if redis-server is installed...
where redis-server >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] redis-server found
    redis-server --version
) else (
    echo [FAIL] redis-server not found in PATH
)

echo.
echo [3/7] Checking if Redis process is running...
tasklist /FI "IMAGENAME eq redis-server.exe" 2>NUL | find /I /N "redis-server.exe">NUL
if %ERRORLEVEL% EQU 0 (
    echo [OK] Redis process is running
) else (
    echo [FAIL] Redis process not found
)

echo.
echo [4/7] Checking if port 6379 is listening...
netstat -an | find "6379" | find "LISTENING" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] Port 6379 is listening
) else (
    echo [FAIL] Port 6379 is not listening
)

echo.
echo [5/7] Testing Redis connection...
redis-cli ping >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] Redis responds to PING
    echo Response:
    redis-cli ping
) else (
    echo [FAIL] Redis did not respond to PING
)

echo.
echo [6/7] Checking Python redis package...
py -c "import redis; print('[OK] Python redis package installed - Version:', redis.__version__)" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [FAIL] Python redis package not found
)

echo.
echo [7/7] Checking environment variables...
if defined REDIS_URL (
    echo [INFO] REDIS_URL = %REDIS_URL%
) else (
    echo [INFO] REDIS_URL not set (will use default)
)

if defined USE_FAKEREDIS (
    echo [INFO] USE_FAKEREDIS = %USE_FAKEREDIS%
) else (
    echo [INFO] USE_FAKEREDIS not set
)

echo.
echo ============================================================
echo   Quick Test via API 
echo ============================================================
echo.
echo Testing health endpoint...
curl -s "http://localhost:8000/api/health" 2>nul
echo.

echo.
echo ============================================================
echo   Summary
echo ============================================================
echo.
echo If you see [OK] for steps 3-5, Redis is working properly!
echo.
echo Installation Options if Redis is not installed:
echo   1. Windows: https://github.com/microsoftarchive/redis/releases
echo   2. WSL: sudo apt install redis-server
echo   3. Docker: docker run -d -p 6379:6379 redis:latest
echo.
pause
