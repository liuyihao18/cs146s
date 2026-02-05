#!/usr/bin/env python3
"""
Run script for Weather MCP Server

This script checks for required dependencies and runs the MCP server.
"""

import os
import sys
from pathlib import Path


def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import mcp
        import httpx
        import dotenv
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e.name}")
        print("\n📦 Please install dependencies first:")
        print("   uv pip install -e .")
        print("   or")
        print("   pip install -e .")
        return False


def check_env_file():
    """Check if .env file exists and has API key"""
    env_file = Path(__file__).parent / ".env"
    
    if not env_file.exists():
        print("❌ .env file not found!")
        print("\n📝 Please create .env file:")
        print("   1. Copy .env.example to .env")
        print("   2. Add your OpenWeatherMap API key")
        print("\nOn Windows:")
        print("   copy .env.example .env")
        print("\nOn macOS/Linux:")
        print("   cp .env.example .env")
        return False
    
    # Check if API key is set
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.getenv("OPENWEATHER_API_KEY")
    
    if not api_key or api_key == "your_api_key_here":
        print("❌ API key not configured!")
        print("\n🔑 Please edit .env file and add your API key:")
        print(f"   Edit: {env_file}")
        print("\nGet your free API key from:")
        print("   https://openweathermap.org/api")
        return False
    
    return True


def main():
    """Main entry point"""
    print("🌤️  Weather MCP Server")
    print("=" * 50)
    
    # Check dependencies
    print("\n1️⃣  Checking dependencies...")
    if not check_dependencies():
        sys.exit(1)
    print("   ✅ Dependencies OK")
    
    # Check environment
    print("\n2️⃣  Checking configuration...")
    if not check_env_file():
        sys.exit(1)
    print("   ✅ Configuration OK")
    
    # Run the server
    print("\n3️⃣  Starting MCP Server...")
    print("-" * 50)
    
    # Import and run main from main.py
    try:
        import main as server_main
        import asyncio
        asyncio.run(server_main.main())
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
