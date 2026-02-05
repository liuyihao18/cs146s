# Weather MCP Server - Quick Start Guide

This guide will help you get the Weather MCP Server up and running in under 5 minutes.

## Quick Setup (3 Steps)

### Step 1: Get API Key (2 minutes)

1. Go to <https://openweathermap.org/api>
2. Click "Sign Up" (top right)
3. Fill in the form (name, email, password)
4. Check your email and verify your account
5. Go to "API keys" tab in your dashboard
6. Copy your API key

### Step 2: Install & Configure (1 minute)

```bash
# Navigate to server directory
cd week3/server

# Install dependencies
uv pip install -e .

# Create .env file
copy .env.example .env

# Edit .env and paste your API key
notepad .env
```

In `.env`, replace `your_api_key_here` with your actual API key:

```env
OPENWEATHER_API_KEY=abc123def456ghi789jkl
```

### Step 3: Test It (1 minute)

```bash
# Run the server
python main.py
```

You should see:

```
INFO - Starting Weather MCP Server...
INFO - Server running on stdio transport
```

Press Ctrl+C to stop.

## Integrate with Claude Desktop (Optional)

### Windows

1. Open: `%APPDATA%\Claude\claude_desktop_config.json`
2. Add this configuration:

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

1. Replace the path with your actual path
2. Replace `your_api_key_here` with your API key
3. Save and restart Claude Desktop

### macOS/Linux

1. Open: `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS)
   or `~/.config/Claude/claude_desktop_config.json` (Linux)
2. Add similar configuration with forward slashes:

```json
{
  "mcpServers": {
    "weather": {
      "command": "python",
      "args": [
        "/Users/yourname/path/to/cs146s/week3/server/main.py"
      ],
      "env": {
        "OPENWEATHER_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

## Test in Claude Desktop

Ask Claude:

- "What's the weather in Paris?"
- "Give me the forecast for Tokyo"
- "Check the air quality in Los Angeles"

Claude will use your MCP server to fetch real weather data!

## Troubleshooting

### Problem: "API key not configured"

**Solution:** Make sure `.env` file exists and contains your API key

### Problem: "Location not found"

**Solution:** Try a different city name or add country code like "Paris,FR"

### Problem: Claude doesn't see the server

**Solution:**

1. Check config file syntax (valid JSON)
2. Use absolute paths (not relative)
3. Completely quit and restart Claude Desktop

### Problem: Server won't start

**Solution:**

1. Check Python version: `python --version` (must be 3.10+)
2. Reinstall dependencies: `uv pip install -e .`
3. Check logs for error messages

## What's Next?

- Read the full [README.md](README.md) for detailed documentation
- Check the [API documentation](https://openweathermap.org/api)
- Customize the server for your needs
- Add more tools or features

## Usage Examples

### Example 1: Current Weather

```
You: What's the current weather in London?

Claude: [uses get_current_weather tool]

Response:
🌍 Weather for London
🌡️ Temperature: 12.5°C
☁️ Condition: Clouds - scattered clouds
💧 Humidity: 65%
...
```

### Example 2: Forecast

```
You: Give me the weather forecast for San Francisco

Claude: [uses get_weather_forecast tool]

Response:
🌍 5-Day Forecast for San Francisco
📅 2026-02-05 15:00
   🌡️ 15.3°C (feels like 14.2°C)
   ☁️ Clear - clear sky
...
```

### Example 3: Air Quality

```
You: How's the air quality in Beijing?

Claude: [uses get_air_quality tool]

Response:
🌫️ Air Quality Index (AQI): 3 - Moderate
Components (μg/m³):
  PM2.5: 35.21
  PM10: 52.34
...
```

## Tips

- **Free tier limit**: 1,000 calls/day - use responsibly
- **City names**: Add country code for accuracy (e.g., "Paris,FR")
- **Coordinates**: Use format "lat,lon" (e.g., "48.8566,2.3522")
- **Units**: Specify celsius, fahrenheit, or kelvin
- **Errors**: Check stderr logs for detailed error messages

## Need Help?

1. Check [README.md](README.md) for full documentation
2. Review [OpenWeatherMap API docs](https://openweathermap.org/api)
3. Check [MCP documentation](https://modelcontextprotocol.io)

---

**Ready to go!** 🚀 Start asking Claude about the weather!
