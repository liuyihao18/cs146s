#!/usr/bin/env python3
"""
Weather MCP Server

A Model Context Protocol server that provides weather data using the OpenWeatherMap API.
Implements multiple tools for getting current weather, forecasts, and air quality data.
"""

import os
import sys
import asyncio
import logging
from typing import Any
from datetime import datetime

import httpx
from dotenv import load_dotenv
from mcp.server import Server
from mcp.types import (
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)
from mcp.server.stdio import stdio_server

# Load environment variables
load_dotenv()

# Configure logging to stderr (STDIO servers must not write to stdout)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("weather-mcp-server")

# API Configuration
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5"
OPENWEATHER_GEO_URL = "https://api.openweathermap.org/geo/1.0"

# Rate limiting configuration
RATE_LIMIT_WARNING = "Note: OpenWeatherMap free tier allows 1,000 calls/day. Please use responsibly."

# Create MCP server instance
app = Server("weather-mcp-server")


class WeatherAPIError(Exception):
    """Custom exception for weather API errors"""

    pass


async def fetch_with_retry(
    client: httpx.AsyncClient,
    url: str,
    params: dict[str, Any],
    max_retries: int = 3,
) -> dict[str, Any]:
    """
    Fetch data from API with retry logic for transient failures.

    Args:
        client: HTTP client instance
        url: API endpoint URL
        params: Query parameters
        max_retries: Maximum number of retry attempts

    Returns:
        JSON response as dictionary

    Raises:
        WeatherAPIError: If request fails after retries
    """
    for attempt in range(max_retries):
        try:
            response = await client.get(url, params=params, timeout=10.0)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise WeatherAPIError(
                    "Invalid API key. Please check your OPENWEATHER_API_KEY environment variable."
                )
            elif e.response.status_code == 404:
                raise WeatherAPIError("Location not found. Please check the city name or coordinates.")
            elif e.response.status_code == 429:
                if attempt < max_retries - 1:
                    logger.warning(f"Rate limit hit, retrying... (attempt {attempt + 1})")
                    await asyncio.sleep(2**attempt)  # Exponential backoff
                    continue
                else:
                    raise WeatherAPIError(
                        "Rate limit exceeded. Please try again later or upgrade your API plan."
                    )
            else:
                raise WeatherAPIError(f"HTTP error {e.response.status_code}: {e.response.text}")
        except httpx.TimeoutException:
            if attempt < max_retries - 1:
                logger.warning(f"Request timeout, retrying... (attempt {attempt + 1})")
                await asyncio.sleep(1)
                continue
            else:
                raise WeatherAPIError("Request timed out after multiple retries.")
        except httpx.RequestError as e:
            raise WeatherAPIError(f"Network error: {str(e)}")

    raise WeatherAPIError("Failed to fetch data after multiple retries")


def format_temperature(kelvin: float, unit: str = "celsius") -> str:
    """Convert temperature from Kelvin to specified unit."""
    if unit == "fahrenheit":
        return f"{(kelvin - 273.15) * 9/5 + 32:.1f}°F"
    elif unit == "kelvin":
        return f"{kelvin:.1f}K"
    else:  # celsius (default)
        return f"{kelvin - 273.15:.1f}°C"


def format_weather_response(data: dict[str, Any], unit: str = "celsius") -> str:
    """Format weather data into a readable string."""
    if not data or "main" not in data:
        return "No weather data available."

    main = data["main"]
    weather = data["weather"][0] if data.get("weather") else {}
    wind = data.get("wind", {})
    clouds = data.get("clouds", {})

    temp = format_temperature(main.get("temp", 0), unit)
    feels_like = format_temperature(main.get("feels_like", 0), unit)
    temp_min = format_temperature(main.get("temp_min", 0), unit)
    temp_max = format_temperature(main.get("temp_max", 0), unit)

    response = f"""
🌍 Weather for {data.get('name', 'Unknown location')}
📅 Time: {datetime.fromtimestamp(data.get('dt', 0)).strftime('%Y-%m-%d %H:%M:%S')}

🌡️ Temperature: {temp}
   Feels like: {feels_like}
   Min: {temp_min} | Max: {temp_max}

☁️ Condition: {weather.get('main', 'Unknown')} - {weather.get('description', 'No description')}
💧 Humidity: {main.get('humidity', 0)}%
🎈 Pressure: {main.get('pressure', 0)} hPa
💨 Wind: {wind.get('speed', 0)} m/s, direction {wind.get('deg', 0)}°
☁️ Cloudiness: {clouds.get('all', 0)}%
"""

    if data.get("rain"):
        response += f"🌧️ Rain (1h): {data['rain'].get('1h', 0)} mm\n"
    if data.get("snow"):
        response += f"❄️ Snow (1h): {data['snow'].get('1h', 0)} mm\n"

    response += f"\n{RATE_LIMIT_WARNING}"
    return response.strip()


def format_forecast_response(data: dict[str, Any], unit: str = "celsius") -> str:
    """Format forecast data into a readable string."""
    if not data or "list" not in data:
        return "No forecast data available."

    city = data.get("city", {})
    forecasts = data.get("list", [])[:8]  # Next 24 hours (3-hour intervals)

    response = f"🌍 5-Day Forecast for {city.get('name', 'Unknown location')}\n"
    response += f"📍 Coordinates: {city.get('coord', {}).get('lat', 0)}, {city.get('coord', {}).get('lon', 0)}\n\n"

    for forecast in forecasts:
        dt = datetime.fromtimestamp(forecast.get("dt", 0))
        main = forecast.get("main", {})
        weather = forecast["weather"][0] if forecast.get("weather") else {}
        wind = forecast.get("wind", {})

        temp = format_temperature(main.get("temp", 0), unit)
        feels_like = format_temperature(main.get("feels_like", 0), unit)

        response += f"📅 {dt.strftime('%Y-%m-%d %H:%M')}\n"
        response += f"   🌡️ {temp} (feels like {feels_like})\n"
        response += f"   ☁️ {weather.get('main', 'Unknown')} - {weather.get('description', 'No description')}\n"
        response += f"   💧 Humidity: {main.get('humidity', 0)}% | 💨 Wind: {wind.get('speed', 0)} m/s\n"
        response += f"   🌧️ Rain probability: {forecast.get('pop', 0) * 100:.0f}%\n\n"

    response += f"{RATE_LIMIT_WARNING}"
    return response.strip()


def format_air_quality_response(data: dict[str, Any]) -> str:
    """Format air quality data into a readable string."""
    if not data or "list" not in data or not data["list"]:
        return "No air quality data available."

    aqi_data = data["list"][0]
    main = aqi_data.get("main", {})
    components = aqi_data.get("components", {})

    aqi_level = main.get("aqi", 0)
    aqi_labels = {
        1: "Good",
        2: "Fair",
        3: "Moderate",
        4: "Poor",
        5: "Very Poor",
    }

    response = f"""
🌫️ Air Quality Index (AQI): {aqi_level} - {aqi_labels.get(aqi_level, 'Unknown')}
📅 Time: {datetime.fromtimestamp(aqi_data.get('dt', 0)).strftime('%Y-%m-%d %H:%M:%S')}

Components (μg/m³):
  CO (Carbon monoxide): {components.get('co', 0):.2f}
  NO (Nitrogen monoxide): {components.get('no', 0):.2f}
  NO₂ (Nitrogen dioxide): {components.get('no2', 0):.2f}
  O₃ (Ozone): {components.get('o3', 0):.2f}
  SO₂ (Sulphur dioxide): {components.get('so2', 0):.2f}
  PM2.5 (Fine particles): {components.get('pm2_5', 0):.2f}
  PM10 (Coarse particles): {components.get('pm10', 0):.2f}
  NH₃ (Ammonia): {components.get('nh3', 0):.2f}

{RATE_LIMIT_WARNING}
"""
    return response.strip()


@app.list_tools()
async def list_tools() -> list[Tool]:
    """
    List all available tools.

    Returns a list of Tool objects defining the available weather tools.
    """
    return [
        Tool(
            name="get_current_weather",
            description="Get current weather conditions for a specific location. "
            "Supports city name or geographic coordinates (latitude/longitude). "
            "Returns temperature, humidity, wind speed, conditions, and more.",
            inputSchema={
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name (e.g., 'London', 'New York,US', 'Tokyo,JP') "
                        "or coordinates in format 'lat,lon' (e.g., '51.5074,-0.1278')",
                    },
                    "units": {
                        "type": "string",
                        "description": "Temperature unit: 'celsius', 'fahrenheit', or 'kelvin'",
                        "enum": ["celsius", "fahrenheit", "kelvin"],
                        "default": "celsius",
                    },
                },
                "required": ["location"],
            },
        ),
        Tool(
            name="get_weather_forecast",
            description="Get 5-day weather forecast with 3-hour intervals for a specific location. "
            "Provides detailed predictions including temperature, conditions, wind, and precipitation probability.",
            inputSchema={
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name (e.g., 'Paris', 'Berlin,DE') "
                        "or coordinates in format 'lat,lon'",
                    },
                    "units": {
                        "type": "string",
                        "description": "Temperature unit: 'celsius', 'fahrenheit', or 'kelvin'",
                        "enum": ["celsius", "fahrenheit", "kelvin"],
                        "default": "celsius",
                    },
                },
                "required": ["location"],
            },
        ),
        Tool(
            name="get_air_quality",
            description="Get current air quality index (AQI) and pollutant concentrations for a specific location. "
            "Provides AQI level (1-5) and detailed measurements of CO, NO, NO2, O3, SO2, PM2.5, PM10, and NH3.",
            inputSchema={
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name or coordinates in format 'lat,lon'",
                    },
                },
                "required": ["location"],
            },
        ),
    ]


async def get_coordinates(location: str, client: httpx.AsyncClient) -> tuple[float, float]:
    """
    Convert location string to coordinates.

    Args:
        location: City name or 'lat,lon' string
        client: HTTP client instance

    Returns:
        Tuple of (latitude, longitude)

    Raises:
        WeatherAPIError: If location cannot be resolved
    """
    # Check if location is already coordinates
    if "," in location:
        try:
            parts = location.split(",")
            lat = float(parts[0].strip())
            lon = float(parts[1].strip())
            if -90 <= lat <= 90 and -180 <= lon <= 180:
                return lat, lon
        except (ValueError, IndexError):
            pass  # Fall through to geocoding

    # Geocode city name
    params = {"q": location, "limit": 1, "appid": OPENWEATHER_API_KEY}
    url = f"{OPENWEATHER_GEO_URL}/direct"

    try:
        data = await fetch_with_retry(client, url, params)
        if not data:
            raise WeatherAPIError(f"Location '{location}' not found.")

        return data[0]["lat"], data[0]["lon"]
    except (KeyError, IndexError) as e:
        raise WeatherAPIError(f"Failed to parse geocoding response: {str(e)}")


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """
    Handle tool execution requests.

    Args:
        name: Name of the tool to execute
        arguments: Dictionary of tool arguments

    Returns:
        List of TextContent with tool results
    """
    # Validate API key
    if not OPENWEATHER_API_KEY:
        logger.error("API key not configured")
        return [
            TextContent(
                type="text",
                text="Error: OPENWEATHER_API_KEY environment variable is not set. "
                "Please configure your API key in the .env file.",
            )
        ]

    # Validate location parameter
    location = arguments.get("location", "").strip()
    if not location:
        return [TextContent(type="text", text="Error: Location parameter is required.")]

    units = arguments.get("units", "celsius")

    try:
        async with httpx.AsyncClient() as client:
            # Get coordinates for the location
            lat, lon = await get_coordinates(location, client)
            logger.info(f"Resolved location '{location}' to coordinates: {lat}, {lon}")

            if name == "get_current_weather":
                # Fetch current weather
                url = f"{OPENWEATHER_BASE_URL}/weather"
                params = {
                    "lat": lat,
                    "lon": lon,
                    "appid": OPENWEATHER_API_KEY,
                }

                data = await fetch_with_retry(client, url, params)
                response_text = format_weather_response(data, units)
                logger.info(f"Successfully fetched current weather for {location}")

                return [TextContent(type="text", text=response_text)]

            elif name == "get_weather_forecast":
                # Fetch weather forecast
                url = f"{OPENWEATHER_BASE_URL}/forecast"
                params = {
                    "lat": lat,
                    "lon": lon,
                    "appid": OPENWEATHER_API_KEY,
                }

                data = await fetch_with_retry(client, url, params)
                response_text = format_forecast_response(data, units)
                logger.info(f"Successfully fetched forecast for {location}")

                return [TextContent(type="text", text=response_text)]

            elif name == "get_air_quality":
                # Fetch air quality data
                url = f"{OPENWEATHER_BASE_URL}/air_pollution"
                params = {
                    "lat": lat,
                    "lon": lon,
                    "appid": OPENWEATHER_API_KEY,
                }

                data = await fetch_with_retry(client, url, params)
                response_text = format_air_quality_response(data)
                logger.info(f"Successfully fetched air quality for {location}")

                return [TextContent(type="text", text=response_text)]

            else:
                logger.warning(f"Unknown tool requested: {name}")
                return [TextContent(type="text", text=f"Error: Unknown tool '{name}'")]

    except WeatherAPIError as e:
        logger.error(f"Weather API error: {str(e)}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return [TextContent(type="text", text=f"Unexpected error: {str(e)}")]


async def main():
    """Run the MCP server using stdio transport."""
    logger.info("Starting Weather MCP Server...")

    if not OPENWEATHER_API_KEY:
        logger.error("OPENWEATHER_API_KEY environment variable is not set!")
        logger.error("Please create a .env file with your API key.")
        sys.exit(1)

    async with stdio_server() as (read_stream, write_stream):
        logger.info("Server running on stdio transport")
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        sys.exit(1)
