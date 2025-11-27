"""
get_data.py - Weather API Integration

This module provides functions to fetch weather data from the National Weather Service API.
All functions are async and designed to work with FastAPI endpoints.

Functions:
- get_weather_data(lat, lon): Fetches 7-day weather forecast for given coordinates
- get_current_conditions(station_id): Gets current weather from a specific station

Note: All functions include proper error handling and require a User-Agent header
      as mandated by the National Weather Service API.
"""

import httpx
from typing import Optional, Dict, Any
from fastapi import HTTPException
import asyncio


async def get_weather_data(latitude: float, longitude: float) -> Dict[str, Any]:
    """
    Fetches weather data from the National Weather Service API.
    
    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate
        
    Returns:
        Dictionary containing weather forecast data
        
    Raises:
        HTTPException: If the API request fails
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # First, get the grid point data
            points_url = f"https://api.weather.gov/points/{latitude},{longitude}"
            points_response = await client.get(
                points_url,
                headers={"User-Agent": "RateLimiterApp/1.0"}
            )
            points_response.raise_for_status()
            points_data = points_response.json()
            
            # Extract forecast URL
            forecast_url = points_data["properties"]["forecast"]
            
            # Get the forecast
            forecast_response = await client.get(
                forecast_url,
                headers={"User-Agent": "RateLimiterApp/1.0"}
            )
            forecast_response.raise_for_status()
            forecast_data = forecast_response.json()
            
            # Format the response
            periods = forecast_data["properties"]["periods"]
            formatted_forecast = []
            
            for period in periods[:7]:  # Get next 7 periods
                formatted_forecast.append({
                    "name": period["name"],
                    "temperature": period["temperature"],
                    "temperatureUnit": period["temperatureUnit"],
                    "windSpeed": period["windSpeed"],
                    "windDirection": period["windDirection"],
                    "shortForecast": period["shortForecast"],
                    "detailedForecast": period["detailedForecast"]
                })
            
            return {
                "location": {
                    "latitude": latitude,
                    "longitude": longitude,
                    "city": points_data["properties"]["relativeLocation"]["properties"]["city"],
                    "state": points_data["properties"]["relativeLocation"]["properties"]["state"]
                },
                "forecast": formatted_forecast,
                "updated": forecast_data["properties"].get("updated", forecast_data["properties"].get("updateTime", "N/A"))
            }
            
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Weather API returned error: {e.response.text}"
        )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Failed to connect to weather API: {str(e)}"
        )
    except KeyError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected API response format: missing {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred: {str(e)}"
        )


async def get_current_conditions(station_id: str) -> Dict[str, Any]:
    """
    Fetches current weather conditions from a specific weather station.
    Args:
        station_id: Weather station identifier (e.g., "KNYC")
    Returns:
        Dictionary containing current weather conditions
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            url = f"https://api.weather.gov/stations/{station_id}/observations/latest"
            response = await client.get(
                url,
                headers={"User-Agent": "RateLimiterApp/1.0"}
            )
            response.raise_for_status()
            data = response.json()
            properties = data["properties"]
            return {
                "station": station_id,
                "timestamp": properties["timestamp"],
                "temperature": {
                    "value": properties["temperature"]["value"],
                    "unit": properties["temperature"]["unitCode"]
                },
                "humidity": properties["relativeHumidity"]["value"],
                "windSpeed": {
                    "value": properties["windSpeed"]["value"],
                    "unit": properties["windSpeed"]["unitCode"]
                },
                "windDirection": properties["windDirection"]["value"],
                "description": properties["textDescription"]
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch current conditions: {str(e)}"
        )
