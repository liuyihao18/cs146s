"""
Test suite for Weather MCP Server

Run with: pytest tests/
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from main import (
    format_temperature,
    format_weather_response,
    format_forecast_response,
    format_air_quality_response,
    get_coordinates,
    WeatherAPIError,
)


class TestTemperatureFormatting:
    """Test temperature conversion functions"""

    def test_kelvin_to_celsius(self):
        result = format_temperature(273.15, "celsius")
        assert result == "0.0°C"

    def test_kelvin_to_fahrenheit(self):
        result = format_temperature(273.15, "fahrenheit")
        assert result == "32.0°F"

    def test_kelvin_to_kelvin(self):
        result = format_temperature(273.15, "kelvin")
        assert result == "273.2K"

    def test_default_celsius(self):
        result = format_temperature(293.15)
        assert result == "20.0°C"


class TestWeatherResponseFormatting:
    """Test weather response formatting"""

    def test_format_weather_response_basic(self):
        data = {
            "name": "London",
            "dt": 1612345678,
            "main": {
                "temp": 283.15,
                "feels_like": 281.15,
                "temp_min": 280.15,
                "temp_max": 285.15,
                "humidity": 65,
                "pressure": 1013,
            },
            "weather": [{"main": "Clouds", "description": "scattered clouds"}],
            "wind": {"speed": 5.5, "deg": 180},
            "clouds": {"all": 40},
        }

        result = format_weather_response(data, "celsius")
        assert "London" in result
        assert "10.0°C" in result
        assert "Clouds" in result
        assert "65%" in result

    def test_format_weather_response_empty(self):
        result = format_weather_response({}, "celsius")
        assert "No weather data available" in result

    def test_format_weather_response_with_rain(self):
        data = {
            "name": "Seattle",
            "dt": 1612345678,
            "main": {"temp": 285.15, "feels_like": 285.15, "temp_min": 285.15, "temp_max": 285.15, "humidity": 80, "pressure": 1010},
            "weather": [{"main": "Rain", "description": "light rain"}],
            "wind": {"speed": 3.0, "deg": 90},
            "clouds": {"all": 90},
            "rain": {"1h": 2.5},
        }

        result = format_weather_response(data, "celsius")
        assert "Seattle" in result
        assert "Rain" in result
        assert "2.5 mm" in result


class TestForecastFormatting:
    """Test forecast response formatting"""

    def test_format_forecast_response(self):
        data = {
            "city": {"name": "Paris", "coord": {"lat": 48.8566, "lon": 2.3522}},
            "list": [
                {
                    "dt": 1612345678,
                    "main": {"temp": 283.15, "feels_like": 281.15, "humidity": 70},
                    "weather": [{"main": "Clear", "description": "clear sky"}],
                    "wind": {"speed": 4.0},
                    "pop": 0.1,
                }
            ],
        }

        result = format_forecast_response(data, "celsius")
        assert "Paris" in result
        assert "48.8566" in result
        assert "10.0°C" in result
        assert "Clear" in result

    def test_format_forecast_response_empty(self):
        result = format_forecast_response({}, "celsius")
        assert "No forecast data available" in result


class TestAirQualityFormatting:
    """Test air quality response formatting"""

    def test_format_air_quality_response(self):
        data = {
            "list": [
                {
                    "dt": 1612345678,
                    "main": {"aqi": 2},
                    "components": {
                        "co": 201.94,
                        "no": 0.01,
                        "no2": 0.78,
                        "o3": 68.66,
                        "so2": 0.64,
                        "pm2_5": 0.5,
                        "pm10": 0.54,
                        "nh3": 0.12,
                    },
                }
            ]
        }

        result = format_air_quality_response(data)
        assert "AQI): 2 - Fair" in result
        assert "201.94" in result  # CO value
        assert "PM2.5" in result

    def test_format_air_quality_response_empty(self):
        result = format_air_quality_response({})
        assert "No air quality data available" in result

    def test_format_air_quality_all_levels(self):
        for aqi_level, label in [
            (1, "Good"),
            (2, "Fair"),
            (3, "Moderate"),
            (4, "Poor"),
            (5, "Very Poor"),
        ]:
            data = {
                "list": [
                    {
                        "dt": 1612345678,
                        "main": {"aqi": aqi_level},
                        "components": {
                            "co": 100.0,
                            "no": 1.0,
                            "no2": 1.0,
                            "o3": 50.0,
                            "so2": 1.0,
                            "pm2_5": 10.0,
                            "pm10": 20.0,
                            "nh3": 1.0,
                        },
                    }
                ]
            }
            result = format_air_quality_response(data)
            assert label in result


@pytest.mark.asyncio
class TestCoordinateResolution:
    """Test coordinate resolution and geocoding"""

    async def test_coordinates_from_string(self):
        """Test parsing coordinates from string"""
        client = AsyncMock()
        lat, lon = await get_coordinates("51.5074,-0.1278", client)
        assert lat == 51.5074
        assert lon == -0.1278
        # Should not call API if coordinates provided
        client.get.assert_not_called()

    async def test_coordinates_from_city_name(self):
        """Test geocoding city name"""
        client = AsyncMock()
        client.get.return_value.json.return_value = [{"lat": 51.5074, "lon": -0.1278}]
        client.get.return_value.raise_for_status = Mock()

        lat, lon = await get_coordinates("London", client)
        assert lat == 51.5074
        assert lon == -0.1278
        client.get.assert_called_once()

    async def test_coordinates_not_found(self):
        """Test error when location not found"""
        client = AsyncMock()
        client.get.return_value.json.return_value = []
        client.get.return_value.raise_for_status = Mock()

        with pytest.raises(WeatherAPIError, match="not found"):
            await get_coordinates("InvalidCity123", client)

    async def test_invalid_coordinates_string(self):
        """Test handling of invalid coordinate strings"""
        client = AsyncMock()
        client.get.return_value.json.return_value = []
        client.get.return_value.raise_for_status = Mock()

        # Should fall back to geocoding
        with pytest.raises(WeatherAPIError):
            await get_coordinates("invalid,coordinates,string", client)


class TestInputValidation:
    """Test input validation"""

    def test_temperature_bounds(self):
        # Test extreme temperatures
        result = format_temperature(0, "kelvin")
        assert "0.0K" in result

        result = format_temperature(373.15, "celsius")
        assert "100.0°C" in result

    def test_coordinate_bounds_valid(self):
        """Test valid coordinate bounds"""
        import asyncio

        client = AsyncMock()

        # Valid coordinates
        lat, lon = asyncio.run(get_coordinates("89.9,-179.9", client))
        assert -90 <= lat <= 90
        assert -180 <= lon <= 180

    def test_empty_location(self):
        """Test empty location string"""
        # This should be caught by the tool handler
        # but we test the geocoding behavior
        pass  # Would need to test the full call_tool function


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
