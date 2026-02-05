# Weather MCP Server - Usage Examples & Demo

This document provides detailed examples of how to use the Weather MCP Server with Claude Desktop or other MCP clients.

## Prerequisites

Before running these examples:

1. Complete the setup (see [QUICKSTART.md](QUICKSTART.md))
2. Configure Claude Desktop with the server
3. Restart Claude Desktop

## Tool Overview

The server provides three tools:

| Tool | Purpose | Key Features |
|------|---------|--------------|
| `get_current_weather` | Current conditions | Temperature, humidity, wind, conditions |
| `get_weather_forecast` | 5-day forecast | 3-hour intervals, 24-hour view |
| `get_air_quality` | Air quality data | AQI level, pollutant measurements |

## Example Conversations

### Example 1: Basic Weather Query

**You:** What's the weather like in Paris today?

**Claude's Response:**
> Let me check the current weather in Paris.
>
> [Uses `get_current_weather` tool]
>
> 🌍 Weather for Paris
> 📅 Time: 2026-02-05 14:30:00
>
> 🌡️ Temperature: 8.5°C
> Feels like: 6.2°C
> Min: 7.0°C | Max: 10.0°C
>
> ☁️ Condition: Clouds - scattered clouds
> 💧 Humidity: 65%
> 🎈 Pressure: 1015 hPa
> 💨 Wind: 3.5 m/s, direction 240°
> ☁️ Cloudiness: 40%
>
> The weather in Paris is quite cool today with scattered clouds. The temperature is around 8-9°C,
> though it feels a bit colder at about 6°C due to the wind. It's moderately cloudy with 40% cloud
> cover. Make sure to dress warmly if you're going outside!

---

### Example 2: Multiple Locations Comparison

**You:** Compare the weather in Tokyo and Seoul

**Claude's Response:**
> I'll check the current weather in both cities.
>
> [Uses `get_current_weather` for Tokyo]
> [Uses `get_current_weather` for Seoul]
>
> **Tokyo:**
>
> - Temperature: 12.3°C (feels like 11.0°C)
> - Condition: Clear sky
> - Humidity: 55%
> - Wind: 2.5 m/s
>
> **Seoul:**
>
> - Temperature: 5.8°C (feels like 3.2°C)
> - Condition: Few clouds
> - Humidity: 62%
> - Wind: 4.0 m/s
>
> Tokyo is noticeably warmer (12°C vs 6°C) and has clearer skies. Seoul is cooler and windier,
> making it feel even colder at around 3°C. If you're traveling between these cities,
> pack accordingly for the 6-degree temperature difference!

---

### Example 3: Planning with Forecast

**You:** I'm visiting London this weekend. What should I expect weather-wise?

**Claude's Response:**
> Let me get the forecast for London.
>
> [Uses `get_weather_forecast` for London]
>
> 🌍 5-Day Forecast for London
>
> Here's what to expect:
>
> **Tomorrow (Feb 6):**
>
> - Morning: 9°C, partly cloudy, 20% rain
> - Afternoon: 11°C, overcast, 40% rain
> - Evening: 8°C, light rain, 60% rain
>
> **Weekend:**
>
> - Saturday: 7-10°C, cloudy with occasional rain (50% probability)
> - Sunday: 8-12°C, clearing up, rain unlikely
>
> **Recommendations:**
>
> - Bring an umbrella, especially for Friday evening and Saturday
> - Layer clothing for temperatures around 8-11°C
> - Sunday looks like the better day for outdoor activities
> - Expect typical London weather - be prepared for quick changes!

---

### Example 4: Air Quality Check

**You:** I'm going for a run in Los Angeles. How's the air quality?

**Claude's Response:**
> Let me check the current air quality in Los Angeles.
>
> [Uses `get_air_quality` for Los Angeles]
>
> 🌫️ Air Quality Index (AQI): 2 - Fair
>
> Key pollutants:
>
> - PM2.5 (Fine particles): 15.3 μg/m³
> - PM10 (Coarse particles): 28.4 μg/m³
> - O₃ (Ozone): 65.2 μg/m³
>
> The air quality in Los Angeles is currently Fair (AQI 2). This is generally acceptable for
> most people. You should be fine for your run, though if you have respiratory sensitivities,
> you might want to avoid strenuous outdoor activities during peak traffic hours.
> The PM2.5 and ozone levels are moderate but within acceptable ranges.

---

### Example 5: Using Coordinates

**You:** What's the weather at coordinates 40.7128, -74.0060?

**Claude's Response:**
> Let me check the weather at those coordinates.
>
> [Uses `get_current_weather` with coordinates]
>
> 🌍 Weather for New York
>
> 🌡️ Temperature: 3.2°C
> Feels like: -1.5°C
> Min: 2.0°C | Max: 5.0°C
>
> ☁️ Condition: Clear - clear sky
> 💧 Humidity: 45%
> 🎈 Pressure: 1018 hPa
> 💨 Wind: 5.2 m/s, direction 310°
> ☁️ Cloudiness: 10%
>
> Those coordinates are in New York City! It's currently quite cold at 3°C, but with the wind,
> it feels below freezing at -1.5°C. Despite the cold, the sky is clear with minimal clouds.
> Dress warmly if you're heading outside!

---

### Example 6: Temperature Unit Preference

**You:** What's the temperature in Miami in Fahrenheit?

**Claude's Response:**
> Let me check Miami's weather with temperature in Fahrenheit.
>
> [Uses `get_current_weather` with units="fahrenheit"]
>
> 🌍 Weather for Miami
>
> 🌡️ Temperature: 78.3°F
> Feels like: 82.5°F
> Min: 75.0°F | Max: 82.0°F
>
> ☁️ Condition: Clear - clear sky
> 💧 Humidity: 72%
> 💨 Wind: 8.5 mph
>
> It's a beautiful day in Miami! Temperature is in the high 70s, though the humidity makes it
> feel like low 80s. Perfect beach weather with clear skies!

---

### Example 7: Multi-Day Planning

**You:** I need to plan outdoor activities in Berlin for the next 3 days. What's the weather looking like?

**Claude's Response:**
> Let me get the detailed forecast for Berlin.
>
> [Uses `get_weather_forecast` for Berlin]
>
> Here's your 3-day outlook for Berlin:
>
> **Day 1 (Today):**
>
> - 09:00: 6°C, overcast, 30% rain
> - 12:00: 8°C, broken clouds, 20% rain  
> - 15:00: 9°C, partly cloudy, 10% rain
> - 18:00: 7°C, clear, 5% rain
> - **Best time:** Afternoon (warmest and clearing)
>
> **Day 2:**
>
> - Morning: 5-7°C, cloudy
> - Afternoon: 8-10°C, scattered clouds
> - Evening: 6°C, partly cloudy
> - **Best time:** Early afternoon
>
> **Day 3:**
>
> - Morning: 4°C, few clouds
> - Afternoon: 9°C, clear sky
> - Evening: 7°C, clear
> - **Best time:** All day looks good!
>
> **Recommendation:** Day 3 is your best bet for outdoor activities - clear skies and
> temperatures reaching 9°C. Day 1 afternoon is also decent. Day 2 is okay but cloudier.

---

### Example 8: Health-Related Air Quality

**You:** I have asthma. Is it safe to exercise outdoors in Beijing today?

**Claude's Response:**
> Let me check Beijing's air quality for you.
>
> [Uses `get_air_quality` for Beijing]
>
> 🌫️ Air Quality Index (AQI): 4 - Poor
>
> Concerning levels:
>
> - PM2.5: 85.2 μg/m³ (High)
> - PM10: 125.4 μg/m³ (High)
> - O₃: 45.3 μg/m³ (Moderate)
>
> **Health Recommendation:**
> Given that you have asthma, I would **not recommend** outdoor exercise in Beijing today.
> The AQI is rated as "Poor" (level 4), with particularly high levels of fine particulate
> matter (PM2.5) that can aggravate respiratory conditions.
>
> **Suggestions:**
>
> - Consider indoor exercise instead
> - If you must go outside, wear an N95 mask
> - Check again later - air quality can improve in the evening
> - Consider rescheduling to a day with better air quality (AQI 1-2)

---

## Advanced Usage Patterns

### Pattern 1: Time-Series Analysis

**Query:** "Track weather changes in San Francisco over the next 24 hours"

The forecast tool provides 3-hour intervals, perfect for tracking weather patterns throughout the day.

### Pattern 2: Travel Planning

**Query:** "I'm flying from New York to London tomorrow. Compare the weather I should expect"

Combines multiple location queries to help with packing and planning.

### Pattern 3: Event Planning

**Query:** "We're planning an outdoor wedding in Paris next Saturday. What are the chances of rain?"

Uses forecast data to check precipitation probability for specific dates.

### Pattern 4: Air Quality Monitoring

**Query:** "What cities between LA, San Francisco, and Portland have the best air quality today?"

Compares AQI across multiple locations for health-conscious decisions.

## Tips for Best Results

### Location Specification

- ✅ Good: "Paris,FR", "New York,US", "Tokyo,JP"
- ✅ Good: "51.5074,-0.1278" (coordinates)
- ⚠️ Okay: "Paris" (might need country for ambiguous names)
- ❌ Avoid: "downtown Paris" (geocoding might fail)

### Temperature Units

- Default is Celsius
- Request "in Fahrenheit" for F
- Request "in Kelvin" for scientific data

### Timing

- Current weather: Real-time data
- Forecast: Updates every 3 hours
- Air quality: Real-time measurements

### Limitations

- Free API tier: 1,000 calls/day
- Forecast limited to 5 days
- Historical data not available
- Some remote locations might have limited data

## Troubleshooting Queries

If Claude says it can't access weather data:

1. **Check if server is configured**: Restart Claude Desktop
2. **Verify location name**: Try adding country code
3. **Try coordinates**: Use lat,lon format
4. **Check API limits**: You might have hit the daily limit

## Testing the Server

You can test individual tools using the MCP Inspector:

```bash
npx @modelcontextprotocol/inspector python main.py
```

This provides a web interface to directly test tool calls without Claude Desktop.

## Integration Notes

- Server runs on STDIO transport
- All logging goes to stderr
- Responses are formatted as TextContent
- Errors are returned gracefully, not as exceptions
- Rate limiting is handled automatically

---

**Happy weather checking!** 🌤️

For more information, see [README.md](README.md) or [QUICKSTART.md](QUICKSTART.md).
