# Rate Limiter Project

A high-performance, scalable Rate Limiter API implemented in Python (FastAPI) and Redis. This project demonstrates four distinct rate-limiting algorithms and includes a real-time dashboard for visualization.

## Features

- **Four Rate Limiting Algorithms**:
    - **Fixed Window Counter**: Simple and memory-efficient, but susceptible to bursts at window boundaries.
    - **Sliding Window Log**: Highly accurate and smooth, but higher memory usage.
    - **Token Bucket**: Allows bursts up to capacity, then smooths out traffic. Ideal for APIs.
    - **Leaky Bucket**: Enforces a constant output rate. Smooths bursts into a steady stream.
- **Real-time Dashboard**: Visualize metrics and test algorithms interactively.
- **Redis-backed**: Uses Redis for distributed state management (supports `fakeredis` for local testing without infrastructure).
- **FastAPI**: Modern, high-performance async framework.

## Architecture

The system is composed of:
1. **FastAPI Backend**: Handles requests and enforces rate limits using a custom Dependency Injection system.
2. **Redis Store**: Stores counters, timestamps, and bucket states.
3. **React Frontend**: A modern, responsive dashboard built with Vite, React, and Tailwind CSS.

## Algorithms Explained

### 1. Fixed Window Counter
Counts requests in a fixed time window (e.g., 60s). If count > limit, reject.
- **Pros**: Simple, low memory.
- **Cons**: "Window boundary problem" allows 2x limit in short time if burst happens at the edge.

### 2. Sliding Window Log
Stores a timestamp for every request. Counts timestamps in the last window.
- **Pros**: Very accurate, no boundary issues.
- **Cons**: High memory cost (stores every request timestamp).

### 3. Sliding Window Counter (Hybrid)
Approximates the count by using a weighted average of the previous window and the current window.
- **Pros**: Memory efficient (only stores 2 counters), smooths out bursts.
- **Cons**: Approximation, assumes uniform distribution in previous window.

### 4. Token Bucket
Tokens are added to a bucket at a fixed rate. Requests consume tokens.
- **Pros**: Allows bursts (up to bucket size), efficient.
- **Cons**: Slightly more complex to implement correctly (race conditions).

### 5. Leaky Bucket
Requests enter a queue and are processed at a constant rate.
- **Pros**: Extremely smooth output rate.
- **Cons**: Bursts are delayed or rejected immediately if queue is full.

## Setup & Running

### Prerequisites
- Python 3.10+
- Node.js 16+
- Redis (optional, falls back to in-memory `fakeredis`)

### Installation

1. Clone the repository.
2. Install Backend dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Install Frontend dependencies:
   ```bash
   cd frontend
   npm install
   ```

### Running Locally

1. Start the Backend (FastAPI):
   ```bash
   uvicorn app.main:app --reload
   ```
   Runs on `http://localhost:8000`.

2. Start the Frontend (Vite):
   ```bash
   cd frontend
   npm run dev
   ```
   Runs on `http://localhost:5173`.

Access the Dashboard at [http://localhost:5173](http://localhost:5173).

### Testing

Run the automated test script to verify all algorithms:
```bash
python test_api.py
```

## API Endpoints

- `GET /api/image/{width}/{height}?algo={algorithm}`
  - Returns a placeholder SVG.
  - `algo` options: `fixed_window`, `sliding_window_log`, `sliding_window_counter`, `token_bucket`, `leaky_bucket`.
- `GET /api/monitor`
  - Returns global and per-algorithm metrics.

## Deployment

A `Dockerfile` is provided for the backend. For the frontend, you would typically build it (`npm run build`) and serve the `dist` folder via FastAPI or Nginx.

