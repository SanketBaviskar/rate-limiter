<#
.SYNOPSIS
    View-RedisData.ps1 - View Redis Store Data

.DESCRIPTION
    This PowerShell script displays all data stored in Redis by the rate limiter.
    It shows keys, types, values, and TTLs in an organized format.

.USAGE
    .\View-RedisData.ps1
#>

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "  REDIS DATA STORE VIEWER" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

# Check if redis-cli is available
try {
    $null = redis-cli --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "redis-cli not working"
    }
} catch {
    Write-Host "ERROR: redis-cli not found in PATH`n" -ForegroundColor Red
    Write-Host "To view Redis data, you need redis-cli installed." -ForegroundColor Yellow
    Write-Host "`nAlternatively, use the API endpoint:" -ForegroundColor Yellow
    Write-Host "  curl http://localhost:8000/api/monitor`n" -ForegroundColor White
    exit 1
}

# Get all keys
Write-Host "Fetching all Redis keys...`n" -ForegroundColor Yellow
$keys = redis-cli KEYS "*" 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Cannot connect to Redis`n" -ForegroundColor Red
    Write-Host "Make sure Redis is running: redis-server`n" -ForegroundColor Yellow
    exit 1
}

if (-not $keys -or $keys.Count -eq 0) {
    Write-Host "Redis is empty - no keys found`n" -ForegroundColor Yellow
    exit 0
}

Write-Host "Found $($keys.Count) keys`n" -ForegroundColor Green
Write-Host "------------------------------------------------------------`n" -ForegroundColor Gray

# Categorize keys
$categories = @{
    "Global Metrics" = @()
    "Fixed Window" = @()
    "Sliding Window Log" = @()
    "Sliding Window Counter" = @()
    "Token Bucket" = @()
    "Leaky Bucket" = @()
    "Active Buckets" = @()
    "Other" = @()
}

foreach ($key in $keys) {
    if ($key -like "global:*") {
        $categories["Global Metrics"] += $key
    }
    elseif ($key -like "*fixed_window*") {
        $categories["Fixed Window"] += $key
    }
    elseif ($key -like "*sliding_window_log*") {
        $categories["Sliding Window Log"] += $key
    }
    elseif ($key -like "*sliding_window_counter*") {
        $categories["Sliding Window Counter"] += $key
    }
    elseif ($key -like "*token_bucket*") {
        $categories["Token Bucket"] += $key
    }
    elseif ($key -like "*leaky_bucket*") {
        $categories["Leaky Bucket"] += $key
    }
    elseif ($key -like "*active_leaky_buckets*") {
        $categories["Active Buckets"] += $key
    }
    else {
        $categories["Other"] += $key
    }
}

# Display each category
foreach ($category in $categories.Keys | Sort-Object) {
    $keyList = $categories[$category]
    if ($keyList.Count -eq 0) { continue }
    
    Write-Host "`n$category ($($keyList.Count) keys)" -ForegroundColor Cyan
    Write-Host "------------------------------------------------------------" -ForegroundColor Gray
    
    foreach ($key in $keyList | Sort-Object) {
        $type = redis-cli TYPE $key 2>&1
        $ttl = redis-cli TTL $key 2>&1
        
        # Format TTL
        if ($ttl -eq "-1") {
            $ttlStr = "No expiration"
        } elseif ($ttl -eq "-2") {
            $ttlStr = "Expired"
        } else {
            $ttlStr = "$ttl seconds"
        }
        
        Write-Host "`n  Key: " -NoNewline -ForegroundColor White
        Write-Host $key -ForegroundColor Yellow
        Write-Host "  Type: " -NoNewline -ForegroundColor White
        Write-Host $type -ForegroundColor Gray
        Write-Host "  TTL: " -NoNewline -ForegroundColor White
        Write-Host $ttlStr -ForegroundColor Gray
        
        # Get value based on type
        if ($type -eq "string") {
            $value = redis-cli GET $key 2>&1
            Write-Host "  Value: " -NoNewline -ForegroundColor White
            Write-Host $value -ForegroundColor Green
        }
        elseif ($type -eq "zset") {
            $count = redis-cli ZCARD $key 2>&1
            Write-Host "  Count: " -NoNewline -ForegroundColor White
            Write-Host $count -ForegroundColor Green
            
            $members = redis-cli ZRANGE $key 0 4 WITHSCORES 2>&1
            if ($members) {
                Write-Host "  Recent timestamps:" -ForegroundColor White
                for ($i = 0; $i -lt $members.Count; $i += 2) {
                    $timestamp = $members[$i + 1]
                    try {
                        $date = [DateTimeOffset]::FromUnixTimeSeconds([long]$timestamp).LocalDateTime
                        Write-Host "    - $date" -ForegroundColor Gray
                    } catch {
                        Write-Host "    - $timestamp" -ForegroundColor Gray
                    }
                }
            }
        }
        elseif ($type -eq "list") {
            $length = redis-cli LLEN $key 2>&1
            Write-Host "  Queue Length: " -NoNewline -ForegroundColor White
            Write-Host $length -ForegroundColor Green
        }
        elseif ($type -eq "set") {
            $members = redis-cli SMEMBERS $key 2>&1
            Write-Host "  Members ($($members.Count)): " -ForegroundColor White
            foreach ($member in $members) {
                Write-Host "    - $member" -ForegroundColor Gray
            }
        }
    }
}

# Summary
Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "  SUMMARY" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

$totalRequests = redis-cli GET "global:total_requests" 2>&1
$total429s = redis-cli GET "global:total_429s" 2>&1
$activeIPs = redis-cli SMEMBERS "global:active_ips" 2>&1

Write-Host "Total Requests: " -NoNewline -ForegroundColor White
Write-Host $(if ($totalRequests) { $totalRequests } else { "0" }) -ForegroundColor Green

Write-Host "Total 429 Responses: " -NoNewline -ForegroundColor White
Write-Host $(if ($total429s) { $total429s } else { "0" }) -ForegroundColor Yellow

Write-Host "Active IPs: " -NoNewline -ForegroundColor White
Write-Host $(if ($activeIPs) { $activeIPs.Count } else { "0" }) -ForegroundColor Cyan
if ($activeIPs) {
    foreach ($ip in $activeIPs) {
        Write-Host "  - $ip" -ForegroundColor Gray
    }
}

Write-Host "`nTotal Keys: " -NoNewline -ForegroundColor White
Write-Host $keys.Count -ForegroundColor Green

Write-Host "`n============================================================`n" -ForegroundColor Cyan
