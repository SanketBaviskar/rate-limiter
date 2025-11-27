# Rate Limiter with Weather API

A FastAPI-based rate limiting service that demonstrates various rate limiting algorithms (Fixed Window, Sliding Window, Token Bucket, Leaky Bucket) with integrated weather data APIs.

## Features

-   **Multiple Rate Limiting Algorithms**:

    -   Fixed Window Counter
    -   Sliding Window Log
    -   Sliding Window Counter
    -   Token Bucket
    -   Leaky Bucket

-   **Weather API Integration**:

    -   Get weather forecasts by latitude/longitude
    -   Get current conditions from weather stations
    -   All weather endpoints are rate-limited

-   **Monitoring Dashboard**: Real-time metrics and visualization

## Quick Start

### Prerequisites

-   Python 3.8+
-   Redis (for rate limiting state)
-   Docker (optional)

### Installation

1. **Install dependencies**:

```bash
pip install -r requirements.txt
```

2. **Start Redis** (if not using Docker):

```bash
redis-server
```

3. **Run the FastAPI server**:

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### Using Docker

```bash
docker-compose up --build
```

## API Endpoints

### Weather Endpoints

#### Get Weather Forecast

```http
GET /api/weather/forecast?latitude={lat}&longitude={lon}
```

**Example**:

```bash
curl "http://localhost:8000/api/weather/forecast?latitude=39.0997&longitude=-94.5786"
```

**Response**:

```json
{
	"location": {
		"latitude": 39.0997,
		"longitude": -94.5786,
		"city": "Kansas City",
		"state": "MO"
	},
	"forecast": [
		{
			"name": "Tonight",
			"temperature": 45,
			"temperatureUnit": "F",
			"windSpeed": "5 mph",
			"windDirection": "N",
			"shortForecast": "Partly Cloudy",
			"detailedForecast": "..."
		}
	],
	"updated": "2025-11-26T19:00:00+00:00"
}
```

#### Get Current Conditions

```http
GET /api/weather/current/{station_id}
```

**Common Station IDs**:

-   `KNYC` - New York City
-   `KLAX` - Los Angeles
-   `KORD` - Chicago
-   `KATL` - Atlanta
-   `KSEA` - Seattle

**Example**:

```bash
curl "http://localhost:8000/api/weather/current/KNYC"
```

### Other Endpoints

#### Placeholder Image (Rate Limited)

```http
GET /api/image/{width}/{height}
```

#### Monitoring Dashboard

```http
GET /api/monitor
```

Returns global metrics and rate limiting statistics.

## Rate Limiting

All API endpoints (except `/api/monitor`) are rate-limited to **10 requests per 60 seconds** by default.

When rate limit is exceeded, you'll receive:

```json
{
	"detail": "Rate limit exceeded. Try again later."
}
```

HTTP Status: `429 Too Many Requests`

## Testing

### Test Weather API

```bash
python test_weather_api.py
```

This will:

-   Test the forecast endpoint
-   Test the current conditions endpoint
-   Test rate limiting behavior

### Manual Testing

1. **Check if server is running**:

```bash
curl http://localhost:8000/
```

2. **Test rate limiting** (send 15 requests quickly):

```bash
for i in {1..15}; do
  curl "http://localhost:8000/api/weather/forecast?latitude=39&longitude=-94"
  echo ""
done
```

## Project Structure

```
.
├── app/
│   ├── main.py              # FastAPI application
│   ├── rate_limiter.py      # Rate limiting algorithms
│   ├── get_data.py          # Weather API integration
│   ├── redis_client.py      # Redis connection
│   └── utils.py             # Utility functions
├── static/
│   └── index.html           # Dashboard UI
├── frontend/                # React dashboard (optional)
├── test_api.py              # API tests
├── test_weather_api.py      # Weather API tests
├── requirements.txt         # Python dependencies
├── Dockerfile               # Docker configuration
└── docker-compose.yml       # Docker Compose setup
```

## Configuration

Rate limiting settings can be configured in `app/main.py`:

```python
rate_limiter = RateLimiter(limit=10, window=60)
```

-   `limit`: Maximum number of requests
-   `window`: Time window in seconds

## Technologies

-   **FastAPI**: Modern Python web framework
-   **Redis**: In-memory data store for rate limiting state
-   **httpx**: Async HTTP client for weather API
-   **National Weather Service API**: Free weather data

## API Documentation

Once the server is running, visit:

-   Swagger UI: `http://localhost:8000/docs`
-   ReDoc: `http://localhost:8000/redoc`

## License

MIT

## Contributing

Feel free to submit issues and enhancement requests!
