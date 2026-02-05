"""Setup configuration for weather-mcp-server"""

from setuptools import setup, find_packages

setup(
    name="weather-mcp-server",
    version="0.1.0",
    description="A Model Context Protocol server for weather data using OpenWeatherMap API",
    py_modules=["main"],
    python_requires=">=3.10",
)
