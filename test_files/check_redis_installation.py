"""
Redis Installation Checker
Checks if Redis server is installed and running on your system
"""
import subprocess
import socket
import sys
import os

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def print_check(description, status, details=""):
    """Print check result"""
    symbol = "[OK]" if status else "[FAIL]"
    print(f"{symbol} {description}")
    if details:
        print(f"      {details}")

def check_redis_cli():
    """Check if redis-cli is installed"""
    print_header("1. Checking Redis CLI Installation")
    try:
        result = subprocess.run(
            ["redis-cli", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            version = result.stdout.strip()
            print_check("Redis CLI is installed", True, version)
            return True
        else:
            print_check("Redis CLI is installed", False, "Command failed")
            return False
    except FileNotFoundError:
        print_check("Redis CLI is installed", False, "redis-cli not found in PATH")
        return False
    except Exception as e:
        print_check("Redis CLI is installed", False, str(e))
        return False

def check_redis_server_installed():
    """Check if redis-server is installed"""
    print_header("2. Checking Redis Server Installation")
    try:
        result = subprocess.run(
            ["redis-server", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            version = result.stdout.strip()
            print_check("Redis Server is installed", True, version)
            return True
        else:
            print_check("Redis Server is installed", False, "Command failed")
            return False
    except FileNotFoundError:
        print_check("Redis Server is installed", False, "redis-server not found in PATH")
        return False
    except Exception as e:
        print_check("Redis Server is installed", False, str(e))
        return False

def check_redis_process():
    """Check if Redis process is running"""
    print_header("3. Checking if Redis is Running")
    
    # Method 1: Try to find process (Windows)
    try:
        result = subprocess.run(
            ["tasklist"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if "redis-server" in result.stdout.lower():
            print_check("Redis process is running", True, "Found in task list")
            return True
    except Exception:
        pass
    
    # Method 2: Try Unix ps command (WSL/Linux)
    try:
        result = subprocess.run(
            ["ps", "aux"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if "redis-server" in result.stdout:
            print_check("Redis process is running", True, "Found in process list")
            return True
    except Exception:
        pass
    
    print_check("Redis process is running", False, "Not found in process list")
    return False

def check_redis_port():
    """Check if Redis port 6379 is listening"""
    print_header("4. Checking Redis Port (6379)")
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('localhost', 6379))
        sock.close()
        
        if result == 0:
            print_check("Port 6379 is listening", True, "Redis port is accessible")
            return True
        else:
            print_check("Port 6379 is listening", False, "Port is not accessible")
            return False
    except Exception as e:
        print_check("Port 6379 is listening", False, str(e))
        return False

def check_redis_connection():
    """Try to connect and ping Redis"""
    print_header("5. Testing Redis Connection")
    
    try:
        result = subprocess.run(
            ["redis-cli", "ping"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 and "PONG" in result.stdout:
            print_check("Redis responds to PING", True, "Connection successful")
            return True
        else:
            print_check("Redis responds to PING", False, f"Response: {result.stdout}")
            return False
    except FileNotFoundError:
        print_check("Redis responds to PING", False, "redis-cli not available")
        return False
    except Exception as e:
        print_check("Redis responds to PING", False, str(e))
        return False

def check_python_redis_package():
    """Check if Python redis package is installed"""
    print_header("6. Checking Python Redis Package")
    
    try:
        import redis
        version = redis.__version__
        print_check("Python redis package installed", True, f"Version {version}")
        return True
    except ImportError:
        print_check("Python redis package installed", False, "Package not found")
        return False

def check_environment_variables():
    """Check Redis-related environment variables"""
    print_header("7. Environment Variables")
    
    redis_url = os.getenv("REDIS_URL")
    use_fake = os.getenv("USE_FAKEREDIS")
    
    if redis_url:
        print_check("REDIS_URL is set", True, redis_url)
    else:
        print_check("REDIS_URL is set", False, "Using default: redis://localhost:6379/0")
    
    if use_fake:
        print_check("USE_FAKEREDIS is set", True, use_fake)
        if use_fake.lower() == "true":
            print("      [WARNING] FakeRedis fallback is enabled")
    else:
        print_check("USE_FAKEREDIS is set", False, "Not set (will use real Redis)")

def provide_installation_instructions():
    """Provide installation instructions if Redis is not installed"""
    print_header("Redis Installation Instructions")
    
    print("\n[INFO] How to Install Redis:\n")
    
    print("Option 1: Windows (Native)")
    print("  1. Download: https://github.com/microsoftarchive/redis/releases")
    print("  2. Extract and run redis-server.exe")
    print("  3. Or use installer from: https://redis.io/download\n")
    
    print("Option 2: Windows (Using WSL)")
    print("  1. Install WSL: wsl --install")
    print("  2. In WSL terminal: sudo apt update")
    print("  3. Install Redis: sudo apt install redis-server")
    print("  4. Start Redis: sudo service redis-server start\n")
    
    print("Option 3: Using Docker")
    print("  1. Install Docker Desktop")
    print("  2. Run: docker run -d -p 6379:6379 redis:latest")
    print("  3. Redis will be available at localhost:6379\n")
    
    print("Option 4: Use FakeRedis (Development Only)")
    print("  1. Set environment variable: $env:USE_FAKEREDIS=\"true\"")
    print("  2. Restart your FastAPI app")
    print("  [WARNING] Note: Data won't persist between restarts\n")

def main():
    """Run all checks"""
    print("\n[CHECK] Redis Installation & Status Checker")
    print("="*60)
    
    checks = {
        "Redis CLI Installed": check_redis_cli(),
        "Redis Server Installed": check_redis_server_installed(),
        "Redis Process Running": check_redis_process(),
        "Port 6379 Accessible": check_redis_port(),
        "Redis Connection Works": check_redis_connection(),
        "Python Package Installed": check_python_redis_package(),
    }
    
    check_environment_variables()
    
    # Summary
    print_header("Summary")
    
    passed = sum(checks.values())
    total = len(checks)
    
    print(f"\n[OK] Passed: {passed}/{total} checks")
    
    if passed == total:
        print("\n[SUCCESS] Redis is fully installed and working!")
        print("          Your application can use Redis for rate limiting.")
    elif checks["Port 6379 Accessible"] and checks["Redis Connection Works"]:
        print("\n[OK] Redis is RUNNING and accessible!")
        print("     Some CLI tools might not be in PATH, but Redis works.")
    elif checks["Python Package Installed"]:
        print("\n[WARNING] Python redis package is installed, but Redis server is NOT running.")
        print("          Your app will fall back to FakeRedis (in-memory only).")
        print("\n[INFO] To start Redis, run: redis-server")
    else:
        print("\n[FAIL] Redis is NOT installed or not running.")
        provide_installation_instructions()
    
    print("\n" + "="*60)
    
    # Return exit code
    return 0 if checks["Redis Connection Works"] else 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nCheck cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
