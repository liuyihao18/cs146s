.PHONY: help install run test clean setup

help:
	@echo "Weather MCP Server - Available Commands"
	@echo "========================================"
	@echo ""
	@echo "  make setup     - Complete setup (install + configure)"
	@echo "  make install   - Install dependencies"
	@echo "  make run       - Run the MCP server"
	@echo "  make test      - Run unit tests"
	@echo "  make clean     - Clean cache files"
	@echo ""

setup: install
	@echo "Setting up environment file..."
	@if not exist .env (copy .env.example .env && echo Created .env file - please add your API key!) else (echo .env file already exists)
	@echo ""
	@echo "Next steps:"
	@echo "1. Edit .env and add your OpenWeatherMap API key"
	@echo "2. Run 'make run' to start the server"

install:
	@echo "Installing dependencies..."
	uv pip install -e .
	@echo "Installation complete!"

run:
	@echo "Starting Weather MCP Server..."
	python run.py

test:
	@echo "Running tests..."
	pytest tests/ -v

clean:
	@echo "Cleaning cache files..."
	@if exist __pycache__ rmdir /s /q __pycache__
	@if exist tests\__pycache__ rmdir /s /q tests\__pycache__
	@if exist .pytest_cache rmdir /s /q .pytest_cache
	@echo "Clean complete!"
