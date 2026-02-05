#!/usr/bin/env python3
"""
Configuration checker for Weather MCP Server

Validates setup and configuration before running the server.
"""

import os
import sys
from pathlib import Path


def print_header(text: str):
    """Print section header"""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}")


def print_status(passed: bool, message: str):
    """Print status message"""
    icon = "✅" if passed else "❌"
    print(f"{icon} {message}")


def check_python_version():
    """Check Python version"""
    print_header("1. Python Version Check")
    
    version = sys.version_info
    required = (3, 10)
    
    current_version = f"{version.major}.{version.minor}.{version.micro}"
    required_version = f"{required[0]}.{required[1]}"
    
    passed = (version.major, version.minor) >= required
    
    print(f"   Current version: Python {current_version}")
    print(f"   Required version: Python {required_version}+")
    print_status(passed, f"Python version requirement")
    
    return passed


def check_dependencies():
    """Check if required packages are installed"""
    print_header("2. Dependencies Check")
    
    required_packages = {
        "mcp": "mcp",
        "httpx": "httpx",
        "dotenv": "python-dotenv",
    }
    
    all_installed = True
    
    for import_name, package_name in required_packages.items():
        try:
            __import__(import_name)
            print_status(True, f"{package_name} installed")
        except ImportError:
            print_status(False, f"{package_name} NOT installed")
            all_installed = False
    
    if not all_installed:
        print("\n   To install dependencies:")
        print("   uv pip install -e .")
        print("   or")
        print("   pip install -e .")
    
    return all_installed


def check_env_file():
    """Check environment configuration"""
    print_header("3. Environment Configuration Check")
    
    server_dir = Path(__file__).parent
    env_file = server_dir / ".env"
    env_example = server_dir / ".env.example"
    
    # Check if .env.example exists
    if env_example.exists():
        print_status(True, ".env.example found")
    else:
        print_status(False, ".env.example NOT found")
        return False
    
    # Check if .env exists
    if not env_file.exists():
        print_status(False, ".env file NOT found")
        print("\n   Create .env file:")
        print(f"   copy {env_example} {env_file}")
        return False
    
    print_status(True, ".env file exists")
    
    # Check if API key is set
    try:
        from dotenv import load_dotenv
        load_dotenv(env_file)
        api_key = os.getenv("OPENWEATHER_API_KEY")
        
        if not api_key:
            print_status(False, "OPENWEATHER_API_KEY not set in .env")
            return False
        
        if api_key == "your_api_key_here":
            print_status(False, "OPENWEATHER_API_KEY still has placeholder value")
            print("\n   Edit .env and replace with your actual API key")
            print("   Get API key from: https://openweathermap.org/api")
            return False
        
        # Mask API key for display
        masked_key = api_key[:4] + "*" * (len(api_key) - 8) + api_key[-4:]
        print_status(True, f"OPENWEATHER_API_KEY configured ({masked_key})")
        
        return True
        
    except Exception as e:
        print_status(False, f"Error reading .env: {e}")
        return False


def check_file_structure():
    """Check if all required files exist"""
    print_header("4. File Structure Check")
    
    server_dir = Path(__file__).parent
    
    required_files = {
        "main.py": "Main server implementation",
        "pyproject.toml": "Project configuration",
        ".gitignore": "Git ignore rules",
        "run.py": "Run script",
    }
    
    all_exist = True
    
    for filename, description in required_files.items():
        file_path = server_dir / filename
        if file_path.exists():
            print_status(True, f"{filename} ({description})")
        else:
            print_status(False, f"{filename} NOT found")
            all_exist = False
    
    return all_exist


def check_main_syntax():
    """Check if main.py has syntax errors"""
    print_header("5. Code Syntax Check")
    
    server_dir = Path(__file__).parent
    main_file = server_dir / "main.py"
    
    if not main_file.exists():
        print_status(False, "main.py not found")
        return False
    
    try:
        with open(main_file, "r", encoding="utf-8") as f:
            code = f.read()
        
        compile(code, str(main_file), "exec")
        print_status(True, "main.py syntax is valid")
        return True
        
    except SyntaxError as e:
        print_status(False, f"Syntax error in main.py: {e}")
        return False
    except Exception as e:
        print_status(False, f"Error checking main.py: {e}")
        return False


def test_api_connection():
    """Test connection to OpenWeatherMap API"""
    print_header("6. API Connection Test")
    
    try:
        from dotenv import load_dotenv
        import httpx
        
        load_dotenv()
        api_key = os.getenv("OPENWEATHER_API_KEY")
        
        if not api_key or api_key == "your_api_key_here":
            print_status(False, "API key not configured - skipping connection test")
            return False
        
        # Test API with a simple request
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": "London",
            "appid": api_key,
        }
        
        print("   Testing API connection to OpenWeatherMap...")
        
        with httpx.Client(timeout=10.0) as client:
            response = client.get(url, params=params)
        
        if response.status_code == 200:
            print_status(True, "API connection successful")
            data = response.json()
            temp_k = data.get("main", {}).get("temp", 0)
            temp_c = temp_k - 273.15
            print(f"   Sample data: London is currently {temp_c:.1f}°C")
            return True
        elif response.status_code == 401:
            print_status(False, "API key is invalid")
            print("   Get a valid API key from: https://openweathermap.org/api")
            return False
        else:
            print_status(False, f"API returned status code {response.status_code}")
            return False
            
    except ImportError as e:
        print_status(False, f"Missing dependency: {e.name}")
        return False
    except Exception as e:
        print_status(False, f"Connection test failed: {e}")
        return False


def print_summary(checks: dict[str, bool]):
    """Print summary of all checks"""
    print_header("Summary")
    
    passed = sum(1 for v in checks.values() if v)
    total = len(checks)
    
    print(f"\n   Checks passed: {passed}/{total}")
    
    if passed == total:
        print("\n   🎉 All checks passed! You're ready to run the server.")
        print("\n   Run the server with:")
        print("   python run.py")
        print("   or")
        print("   python main.py")
    else:
        print("\n   ⚠️  Some checks failed. Please fix the issues above.")
        print("\n   Failed checks:")
        for name, passed in checks.items():
            if not passed:
                print(f"      - {name}")
    
    return passed == total


def main():
    """Run all checks"""
    print("🌤️  Weather MCP Server - Configuration Checker")
    
    checks = {
        "Python version": check_python_version(),
        "Dependencies": check_dependencies(),
        "Environment config": check_env_file(),
        "File structure": check_file_structure(),
        "Code syntax": check_main_syntax(),
        "API connection": test_api_connection(),
    }
    
    success = print_summary(checks)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
