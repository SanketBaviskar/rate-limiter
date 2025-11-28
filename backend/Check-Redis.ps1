<#
.SYNOPSIS
    Check-Redis.ps1 - Redis Installation and Status Checker

.DESCRIPTION
    This PowerShell script performs comprehensive checks to verify if Redis is properly
    installed and running on your system. It checks:
    - Redis CLI installation
    - Redis Server installation  
    - Redis process status
    - Port 6379 connectivity
    - Redis PING response
    - Python redis package
    - FastAPI health endpoint

.USAGE
    .\Check-Redis.ps1

.NOTES
    Requires PowerShell 5.1 or higher
    Colorized output for easy reading
#>

# Redis Installation Checker - PowerShell Version
Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "  Redis Installation & Status Check" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

$checks = @{
    "Redis CLI" = $false
    "Redis Server" = $false  
    "Redis Process" = $false
    "Port 6379" = $false
    "Redis Connection" = $false
    "Python Package" = $false
}

# Check 1: Redis CLI
Write-Host "[1/6] Checking redis-cli..." -ForegroundColor Yellow
try {
    $version = redis-cli --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] " -ForegroundColor Green -NoNewline
        Write-Host "redis-cli is installed: $version"
        $checks["Redis CLI"] = $true
    } else {
        Write-Host "[FAIL] " -ForegroundColor Red -NoNewline
        Write-Host "redis-cli not working"
    }
} catch {
    Write-Host "[FAIL] " -ForegroundColor Red -NoNewline
    Write-Host "redis-cli not found in PATH"
}

# Check 2: Redis Server
Write-Host "`n[2/6] Checking redis-server..." -ForegroundColor Yellow
try {
    $version = redis-server --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] " -ForegroundColor Green -NoNewline
        Write-Host "redis-server is installed: $version"
        $checks["Redis Server"] = $true
    } else {
        Write-Host "[FAIL] " -ForegroundColor Red -NoNewline
        Write-Host "redis-server not working"
    }
} catch {
    Write-Host "[FAIL] " -ForegroundColor Red -NoNewline
    Write-Host "redis-server not found in PATH"
}

# Check 3: Redis Process
Write-Host "`n[3/6] Checking if Redis is running..." -ForegroundColor Yellow
$process = Get-Process -Name "redis-server" -ErrorAction SilentlyContinue
if ($process) {
    Write-Host "[OK] " -ForegroundColor Green -NoNewline
    Write-Host "Redis process is running (PID: $($process.Id))"
    $checks["Redis Process"] = $true
} else {
    Write-Host "[FAIL] " -ForegroundColor Red -NoNewline
    Write-Host "Redis process not found"
}

# Check 4: Port 6379
Write-Host "`n[4/6] Checking port 6379..." -ForegroundColor Yellow
$port = Test-NetConnection -ComputerName localhost -Port 6379 -InformationLevel Quiet -WarningAction SilentlyContinue
if ($port) {
    Write-Host "[OK] " -ForegroundColor Green -NoNewline
    Write-Host "Port 6379 is listening"
    $checks["Port 6379"] = $true
} else {
    Write-Host "[FAIL] " -ForegroundColor Red -NoNewline
    Write-Host "Port 6379 is not accessible"
}

# Check 5: Redis Connection
Write-Host "`n[5/6] Testing Redis connection with PING..." -ForegroundColor Yellow
try {
    $response = redis-cli ping 2>&1
    if ($response -like "*PONG*") {
        Write-Host "[OK] " -ForegroundColor Green -NoNewline
        Write-Host "Redis responds: $response"
        $checks["Redis Connection"] = $true
    } else {
        Write-Host "[FAIL] " -ForegroundColor Red -NoNewline
        Write-Host "Unexpected response: $response"
    }
} catch {
    Write-Host "[FAIL] " -ForegroundColor Red -NoNewline
    Write-Host "Cannot connect to Redis"
}

# Check 6: Python Package
Write-Host "`n[6/6] Checking Python redis package..." -ForegroundColor Yellow
try {
    $pythonCheck = py -c "import redis; print(redis.__version__)" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] " -ForegroundColor Green -NoNewline
        Write-Host "Python redis package installed (v$pythonCheck)"
        $checks["Python Package"] = $true
    } else {
        Write-Host "[FAIL] " -ForegroundColor Red -No newline
        Write-Host "Python redis package not found"
    }
} catch {
    Write-Host "[FAIL] " -ForegroundColor Red -NoNewline
    Write-Host "Error checking Python package"
}

# API Health Check
Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "  API Health Check" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/api/health" -ErrorAction Stop
    Write-Host "[OK] " -ForegroundColor Green -NoNewline
    Write-Host "API is running"
    Write-Host "     Status: $($health.status)" -ForegroundColor White
    Write-Host "     Redis Connected: $($health.redis.connected)" -ForegroundColor White
    Write-Host "     Using FakeRedis: $($health.redis.is_fakeredis)" -ForegroundColor White
    Write-Host "     Redis Type: $($health.redis.type)" -ForegroundColor White
} catch {
    Write-Host "[FAIL] " -ForegroundColor Red -NoNewline
    Write-Host "Cannot connect to API at http://localhost:8000"
}

# Summary
Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "  Summary" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

$passed = ($checks.Values | Where-Object { $_ -eq $true }).Count
$total = $checks.Count

Write-Host "Passed: $passed/$total checks`n" -ForegroundColor $(if ($passed -eq $total) { "Green" } else { "Yellow" })

foreach ($check in $checks.GetEnumerator()) {
    $status = if ($check.Value) { "[OK]" } else { "[FAIL]" }
    $color = if ($check.Value) { "Green" } else { "Red" }
    Write-Host "$status" -ForegroundColor $color -NoNewline
    Write-Host " $($check.Name)"
}

Write-Host "`n------------------------------------------------------------" -ForegroundColor Gray

if ($checks["Redis Connection"]) {
    Write-Host "`n[SUCCESS] Redis is installed and working!" -ForegroundColor Green
    Write-Host "          Your application can use Redis for rate limiting.`n" -ForegroundColor Green
} elseif ($checks["Python Package"]) {
    Write-Host "`n[WARNING] Redis server is NOT running!" -ForegroundColor Yellow
    Write-Host "          Your app will use FakeRedis (in-memory fallback)" -ForegroundColor Yellow
    Write-Host "`n[INFO] To start Redis:" -ForegroundColor Cyan
    Write-Host "       redis-server`n" -ForegroundColor White
} else {
    Write-Host "`n[FAIL] Redis is NOT installed!" -ForegroundColor Red
    Write-Host "`n[INFO] Installation options:" -ForegroundColor Cyan
    Write-Host "  1. Windows: https://github.com/microsoftarchive/redis/releases" -ForegroundColor White
    Write-Host "  2. WSL: sudo apt install redis-server" -ForegroundColor White
    Write-Host "  3. Docker: docker run -d -p 6379:6379 redis:latest`n" -ForegroundColor White
}

Write-Host "============================================================`n" -ForegroundColor Cyan
