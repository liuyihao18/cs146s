# Weather MCP Server

A Model Context Protocol (MCP) server that provides weather data using the OpenWeatherMap API. This server exposes three tools for accessing current weather conditions, forecasts, and air quality information for any location worldwide.

## Features

- **Three Weather Tools**:
  - `get_current_weather`: Real-time weather conditions
  - `get_weather_forecast`: 5-day forecast with 3-hour intervals
  - `get_air_quality`: Air quality index and pollutant measurements

- **Robust Error Handling**:
  - Graceful handling of HTTP failures and timeouts
  - Exponential backoff for rate limits
  - Clear error messages for invalid inputs
  - Comprehensive input validation

- **Developer-Friendly**:
  - Type hints throughout
  - Detailed logging (stderr only, STDIO-compliant)
  - Easy setup with environment variables
  - Support for multiple temperature units

## Prerequisites

- Python 3.10 or higher
- OpenWeatherMap API key (free tier available)
- `uv` package manager (recommended) or `pip`

## Setup Instructions

### 1. Get an OpenWeatherMap API Key

1. Visit [OpenWeatherMap](https://openweathermap.org/api)
2. Sign up for a free account
3. Generate an API key from your account dashboard
4. The free tier includes:
   - 1,000 API calls per day
   - Current weather data
   - 5-day/3-hour forecasts
   - Air quality data

### 2. Install Dependencies

Navigate to the server directory:

```bash
cd week3/server
```

**Using `uv` (recommended):**

```bash
uv venv
uv pip install -e .
```

**Using `pip`:**

```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

pip install -e .
```

### 3. Configure Environment Variables

Create a `.env` file in the `week3/server` directory:

```bash
cp .env.example .env
```

Edit `.env` and add your API key:

```env
OPENWEATHER_API_KEY=your_actual_api_key_here
```

### 4. Test the Server

Run the server directly to verify it works:

```bash
python main.py
```

The server will start in STDIO mode. You should see log messages like:

```
2026-02-05 10:30:00 - weather-mcp-server - INFO - Starting Weather MCP Server...
2026-02-05 10:30:00 - weather-mcp-server - INFO - Server running on stdio transport
```

Press `Ctrl+C` to stop the server.

## Integration with Claude Desktop

To use this server with Claude Desktop:

### 1. Locate Claude Desktop Configuration

**Windows:**

```
%APPDATA%\Claude\claude_desktop_config.json
```

**macOS:**

```
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Linux:**

```
~/.config/Claude/claude_desktop_config.json
```

### 2. Update Configuration

Add the following to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "weather": {
      "command": "python",
      "args": [
        "C:\\Users\\Spring\\Documents\\Program\\AI\\cs146s\\week3\\server\\main.py"
      ],
      "env": {
        "OPENWEATHER_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

**Important:** Use absolute paths and replace `C:\\Users\\Spring\\Documents\\Program\\AI\\cs146s` with your actual workspace path.

### 3. Restart Claude Desktop

Completely quit and restart Claude Desktop to load the new MCP server.

### 4. Verify Integration

In Claude Desktop, you should now see the weather tools available. The tools will appear in the tool list when relevant to your conversation.

## Tool Reference

### 1. get_current_weather

Get current weather conditions for any location.

**Parameters:**

- `location` (required): City name or coordinates
  - Examples: `"London"`, `"New York,US"`, `"Tokyo,JP"`, `"51.5074,-0.1278"`
- `units` (optional): Temperature unit
  - Options: `"celsius"` (default), `"fahrenheit"`, `"kelvin"`

**Example Request:**

```json
{
  "location": "Paris,FR",
  "units": "celsius"
}
```

**Example Output:**

```
🌍 Weather for Paris
📅 Time: 2026-02-05 14:30:00

🌡️ Temperature: 8.5°C
   Feels like: 6.2°C
   Min: 7.0°C | Max: 10.0°C

☁️ Condition: Clouds - scattered clouds
💧 Humidity: 65%
🎈 Pressure: 1015 hPa
💨 Wind: 3.5 m/s, direction 240°
☁️ Cloudiness: 40%
```

### 2. get_weather_forecast

Get 5-day forecast with 3-hour intervals.

**Parameters:**

- `location` (required): City name or coordinates
- `units` (optional): Temperature unit (celsius/fahrenheit/kelvin)

**Example Request:**

```json
{
  "location": "Berlin,DE",
  "units": "fahrenheit"
}
```

**Example Output:**

```
🌍 5-Day Forecast for Berlin
📍 Coordinates: 52.5200, 13.4050

📅 2026-02-05 15:00
   🌡️ 45.3°F (feels like 41.2°F)
   ☁️ Clouds - broken clouds
   💧 Humidity: 72% | 💨 Wind: 4.2 m/s
   🌧️ Rain probability: 30%

📅 2026-02-05 18:00
   🌡️ 42.1°F (feels like 38.5°F)
   ☁️ Clear - clear sky
   💧 Humidity: 68% | 💨 Wind: 3.8 m/s
   🌧️ Rain probability: 10%

[... more forecast entries ...]
```

### 3. get_air_quality

Get current air quality index and pollutant measurements.

**Parameters:**

- `location` (required): City name or coordinates

**Example Request:**

```json
{
  "location": "Beijing"
}
```

**Example Output:**

```
🌫️ Air Quality Index (AQI): 3 - Moderate
📅 Time: 2026-02-05 14:30:00

Components (μg/m³):
  CO (Carbon monoxide): 450.32
  NO (Nitrogen monoxide): 12.45
  NO₂ (Nitrogen dioxide): 45.67
  O₃ (Ozone): 78.90
  SO₂ (Sulphur dioxide): 23.45
  PM2.5 (Fine particles): 35.21
  PM10 (Coarse particles): 52.34
  NH₃ (Ammonia): 5.67
```

**AQI Levels:**

- 1: Good
- 2: Fair
- 3: Moderate
- 4: Poor
- 5: Very Poor

## Usage Examples

### Example 1: Check Current Weather

**In Claude Desktop, ask:**
> "What's the current weather in London?"

Claude will use the `get_current_weather` tool and provide formatted weather information.

### Example 2: Get Forecast

**In Claude Desktop, ask:**
> "Give me the weather forecast for San Francisco for the next few days"

Claude will use the `get_weather_forecast` tool to retrieve and present the forecast.

### Example 3: Check Air Quality

**In Claude Desktop, ask:**
> "How's the air quality in Los Angeles?"

Claude will use the `get_air_quality` tool to get AQI and pollutant data.

### Example 4: Multiple Locations

**In Claude Desktop, ask:**
> "Compare the weather in Tokyo and Seoul"

Claude will call the tool multiple times to compare weather conditions.

## Error Handling

The server implements comprehensive error handling:

### Invalid API Key

```
Error: Invalid API key. Please check your OPENWEATHER_API_KEY environment variable.
```

### Location Not Found

```
Error: Location not found. Please check the city name or coordinates.
```

### Rate Limit Exceeded

```
Error: Rate limit exceeded. Please try again later or upgrade your API plan.
```

The server automatically retries transient failures with exponential backoff.

## Rate Limits

The OpenWeatherMap free tier allows:

- **1,000 API calls per day**
- **60 calls per minute**

The server displays a reminder with each response to use the API responsibly.

## Project Structure

```
week3/server/
├── main.py                 # Main MCP server implementation
├── pyproject.toml          # Project dependencies and metadata
├── .env.example            # Example environment configuration
├── .env                    # Your actual API key (not in git)
└── .gitignore             # Git ignore patterns
```

## Technical Implementation

### MCP Protocol Compliance

- **STDIO Transport**: Uses standard input/output for communication
- **No stdout pollution**: All logging goes to stderr
- **Proper tool definitions**: Typed parameters with JSON Schema
- **Error handling**: Returns errors as TextContent, not exceptions

### API Integration

- **Base URL**: `https://api.openweathermap.org/data/2.5`
- **Geocoding**: Converts city names to coordinates
- **Endpoints**:
  - `/weather` - Current weather
  - `/forecast` - 5-day forecast
  - `/air_pollution` - Air quality data

### Reliability Features

1. **Retry Logic**: Automatic retries with exponential backoff
2. **Timeout Handling**: 10-second timeout with retries
3. **Input Validation**: Validates all required parameters
4. **Coordinate Parsing**: Supports both city names and lat/lon
5. **Rate Limit Awareness**: Warns users about API limits

## Development

### Running Tests

(Tests can be added in the future)

```bash
pytest tests/
```

### Debugging

Enable verbose logging by modifying the logging level in `main.py`:

```python
logging.basicConfig(level=logging.DEBUG, ...)
```

### Testing with MCP Inspector

Use the official MCP inspector tool to test your server:

```bash
npx @modelcontextprotocol/inspector python main.py
```

This provides a web UI for testing tools without Claude Desktop.

## Troubleshooting

### Server doesn't start

1. **Check API key**: Verify `OPENWEATHER_API_KEY` is set in `.env`
2. **Check dependencies**: Run `uv pip install -e .` again
3. **Check logs**: Look at stderr output for error messages

### Claude Desktop doesn't see the server

1. **Verify config path**: Ensure `claude_desktop_config.json` is in the right location
2. **Check JSON syntax**: Validate your config file syntax
3. **Use absolute paths**: Replace relative paths with absolute paths
4. **Restart completely**: Fully quit and restart Claude Desktop

### API errors

1. **401 Unauthorized**: Invalid API key
2. **404 Not Found**: Invalid location name
3. **429 Too Many Requests**: Rate limit exceeded

## API Documentation

- [OpenWeatherMap API Docs](https://openweathermap.org/api)
- [Current Weather API](https://openweathermap.org/current)
- [5-Day Forecast API](https://openweathermap.org/forecast5)
- [Air Pollution API](https://openweathermap.org/api/air-pollution)

## MCP Resources

- [MCP Specification](https://modelcontextprotocol.io/specification)
- [MCP Server Quickstart](https://modelcontextprotocol.io/quickstart/server)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)

## License

This project is created for educational purposes as part of CS146 coursework.

## Author

Created for CS146 Week 3 Assignment
