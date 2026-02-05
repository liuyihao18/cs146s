# Installation Guide - Weather MCP Server

Complete step-by-step installation instructions for the Weather MCP Server.

## System Requirements

- **Python**: 3.10 or higher
- **Operating System**: Windows, macOS, or Linux
- **Package Manager**: `uv` (recommended) or `pip`
- **Internet**: Required for API access

## Installation Steps

### Step 1: Verify Python Version

Open a terminal and check your Python version:

```bash
python --version
```

or

```bash
python3 --version
```

You should see Python 3.10 or higher. If not, download from [python.org](https://www.python.org/downloads/).

### Step 2: Navigate to Server Directory

```bash
cd week3/server
```

### Step 3: Install Package Manager (if needed)

#### Option A: Using uv (Recommended)

Install `uv` if you don't have it:

```bash
# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### Option B: Using pip (Alternative)

`pip` comes with Python, so no installation needed.

### Step 4: Create Virtual Environment (Optional but Recommended)

#### Using uv

```bash
uv venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
```

#### Using pip

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### Step 5: Install Dependencies

#### Using uv

```bash
uv pip install -e .
```

#### Using pip

```bash
pip install -e .
```

This will install:

- `mcp` - Model Context Protocol SDK
- `httpx` - HTTP client
- `python-dotenv` - Environment configuration

### Step 6: Get OpenWeatherMap API Key

1. Go to <https://openweathermap.org/api>
2. Click "Sign Up" in the top right
3. Fill out the registration form:
   - Email address
   - Password
   - Username
4. Verify your email address
5. Log in to your account
6. Go to "API keys" section
7. Copy your default API key (or generate a new one)

**Important**: The free tier provides:

- 1,000 API calls per day
- 60 calls per minute
- No credit card required!

### Step 7: Configure Environment Variables

Create `.env` file:

```bash
# Windows:
copy .env.example .env

# macOS/Linux:
cp .env.example .env
```

Edit `.env` file and add your API key:

```env
OPENWEATHER_API_KEY=your_actual_api_key_here
```

**Replace** `your_actual_api_key_here` with the API key you copied from OpenWeatherMap.

### Step 8: Verify Installation

Run the setup checker:

```bash
python check_setup.py
```

This will verify:

- ✅ Python version (3.10+)
- ✅ Dependencies installed
- ✅ `.env` file configured
- ✅ File structure complete
- ✅ Code syntax valid
- ✅ API connection working

If all checks pass, you're ready to go!

## Running the Server

### Option 1: Using Run Script (Recommended)

```bash
python run.py
```

This script includes pre-flight checks before starting the server.

### Option 2: Direct Execution

```bash
python main.py
```

### Option 3: Using Make (if you have `make` installed)

```bash
make run
```

## Expected Output

When the server starts successfully:

```
🌤️  Weather MCP Server
==================================================

1️⃣  Checking dependencies...
   ✅ Dependencies OK

2️⃣  Checking configuration...
   ✅ Configuration OK

3️⃣  Starting MCP Server...
--------------------------------------------------
2026-02-05 10:30:00 - weather-mcp-server - INFO - Starting Weather MCP Server...
2026-02-05 10:30:00 - weather-mcp-server - INFO - Server running on stdio transport
```

The server is now running! Press `Ctrl+C` to stop.

## Troubleshooting Installation

### Issue: "Python version too old"

**Solution**: Install Python 3.10 or higher from [python.org](https://www.python.org/downloads/)

### Issue: "uv: command not found"

**Solution**: Either:

1. Install `uv` using the commands in Step 3
2. Use `pip` instead (see Option B)

### Issue: "pip: command not found"

**Solution**: Reinstall Python with "Add Python to PATH" option checked

### Issue: "No module named 'mcp'"

**Solution**: Dependencies not installed. Run:

```bash
uv pip install -e .
# or
pip install -e .
```

### Issue: "Permission denied" when installing

**Solution**:

- Use virtual environment (Step 4)
- Or add `--user` flag: `pip install --user -e .`
- Or run with admin/sudo (not recommended)

### Issue: ".env file not found"

**Solution**: Create it:

```bash
copy .env.example .env   # Windows
cp .env.example .env     # macOS/Linux
```

### Issue: "Invalid API key"

**Solution**:

1. Check `.env` file has correct key
2. Wait a few minutes (new keys need activation)
3. Generate a new key from OpenWeatherMap dashboard

### Issue: "Connection refused" or "Network error"

**Solution**:

1. Check internet connection
2. Check firewall settings
3. Verify OpenWeatherMap API is accessible: <https://openweathermap.org/api>

## Installing Development Dependencies

For running tests and development:

```bash
# Using uv:
uv pip install -e ".[dev]"

# Using pip:
pip install -e ".[dev]"
```

This installs additional packages:

- `pytest` - Testing framework
- `pytest-asyncio` - Async test support

## Running Tests

After installing dev dependencies:

```bash
pytest tests/ -v
```

## Updating Dependencies

To update to latest versions:

```bash
# Using uv:
uv pip install --upgrade -e .

# Using pip:
pip install --upgrade -e .
```

## Uninstallation

To remove the server:

```bash
# Deactivate virtual environment (if using one)
deactivate

# Remove virtual environment
# Windows:
rmdir /s .venv
# macOS/Linux:
rm -rf .venv

# Or if installed globally:
pip uninstall mcp httpx python-dotenv
```

## Platform-Specific Notes

### Windows

- Use PowerShell or Command Prompt
- Use backslashes in paths: `week3\server`
- Activate venv: `.venv\Scripts\activate`

### macOS

- Use Terminal
- Use forward slashes in paths: `week3/server`
- Activate venv: `source .venv/bin/activate`
- May need `python3` instead of `python`

### Linux

- Use Terminal
- Use forward slashes in paths: `week3/server`
- Activate venv: `source .venv/bin/activate`
- May need `python3` and `pip3`

## Docker Installation (Advanced)

If you prefer Docker:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install -e .

ENV OPENWEATHER_API_KEY=your_key_here

CMD ["python", "main.py"]
```

Build and run:

```bash
docker build -t weather-mcp-server .
docker run -it weather-mcp-server
```

## Next Steps

After successful installation:

1. **Test the server**: Run `python main.py` to verify it works
2. **Integrate with Claude**: See [README.md](README.md) for Claude Desktop setup
3. **Read usage guide**: Check [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md) for examples
4. **Start using**: Ask Claude about weather!

## Getting Help

If you encounter issues:

1. Run `python check_setup.py` to diagnose problems
2. Check error messages in terminal
3. Verify all installation steps were followed
4. Check [README.md](README.md) troubleshooting section
5. Ensure API key is valid and activated

## Quick Installation Summary

For experienced users:

```bash
cd week3/server
uv venv && source .venv/bin/activate  # or .venv\Scripts\activate on Windows
uv pip install -e .
cp .env.example .env
# Edit .env with your API key
python check_setup.py
python run.py
```

Done! 🎉

---

**Need more help?** See [README.md](README.md) or [QUICKSTART.md](QUICKSTART.md)
