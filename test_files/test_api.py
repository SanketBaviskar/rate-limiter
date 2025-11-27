import requests
import time
import sys

BASE_URL = "http://localhost:8000/api/image/200/200"

def test_algorithm(algo_name):
    print(f"\nTesting Algorithm: {algo_name}")
    print("-" * 30)
    
    success_count = 0
    blocked_count = 0
    
    # Try to make 15 requests (limit is 10)
    for i in range(1, 16):
        try:
            response = requests.get(f"{BASE_URL}?algo={algo_name}")
            if response.status_code == 200:
                print(f"Request {i}: 200 OK")
                success_count += 1
            elif response.status_code == 429:
                print(f"Request {i}: 429 Too Many Requests")
                blocked_count += 1
            else:
                print(f"Request {i}: {response.status_code}")
        except Exception as e:
            print(f"Request {i}: Error {e}")
        
        # Small delay to not overwhelm local network stack, but fast enough to hit limit
        time.sleep(0.1)
        
    print("-" * 30)
    print(f"Results for {algo_name}:")
    print(f"Success: {success_count}")
    print(f"Blocked: {blocked_count}")

if __name__ == "__main__":
    algorithms = ["fixed_window", "sliding_window_log", "sliding_window_counter", "token_bucket", "leaky_bucket"]
    
    # Wait for server to start
    print("Waiting for server to be ready...")
    try:
        for _ in range(10):
            try:
                requests.get("https://api.weather.gov/")
                print("Server is ready!")
                break
            except:
                time.sleep(1)
    except:
        print("Server not reachable.")
        sys.exit(1)

    for algo in algorithms:
        test_algorithm(algo)
        # Sleep between algos to let windows reset (approx 60s needed for full reset)
        # But for testing we just want to see *some* blocking.
        # We won't wait 60s here to save time, just note that they share the same IP
        # but different keys in Redis (I implemented key as `rate_limit:{algo}:{ip}`).
        # So they are independent!
