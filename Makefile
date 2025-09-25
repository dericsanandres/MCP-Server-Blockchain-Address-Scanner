# Makefile for MCP Etherscan Server

VENV_NAME := venv
PYTHON := python3.12
VENV_PYTHON := $(VENV_NAME)/bin/python
VENV_PIP := $(VENV_NAME)/bin/pip

# Check Python version
PYTHON_VERSION := $(shell $(PYTHON) -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
REQUIRED_VERSION := 3.10

# Default target
.PHONY: help
help:
	@echo "Available targets:"
	@echo "  setup     - Create virtual environment and install dependencies"
	@echo "  install   - Install dependencies in existing venv"
	@echo "  run       - Run the MCP server"
	@echo "  dev       - Install in development mode"
	@echo "  clean     - Remove virtual environment"
	@echo "  test      - Run tests (if available)"
	@echo "  lint      - Run code linting"
	@echo "  env       - Show environment info"

# Check Python version
.PHONY: check-python
check-python:
	@echo "Checking Python version..."
	@echo "Found: Python $(PYTHON_VERSION)"
	@echo "Required: Python $(REQUIRED_VERSION)+"
	@if [ "$(shell echo "$(PYTHON_VERSION) >= $(REQUIRED_VERSION)" | bc -l)" != "1" ] 2>/dev/null; then \
		echo "ERROR: Python $(REQUIRED_VERSION)+ required. Found $(PYTHON_VERSION)"; \
		echo "Please install Python $(REQUIRED_VERSION) or higher"; \
		exit 1; \
	fi

# Create virtual environment and install dependencies
.PHONY: setup
setup: check-python $(VENV_NAME)
	@echo "Setup complete! Run 'make run' to start the server"
	@echo "Don't forget to configure your .env file with ETHERSCAN_API_KEY"

$(VENV_NAME): check-python
	@echo "Creating virtual environment..."
	$(PYTHON) -m venv $(VENV_NAME)
	@echo "Installing dependencies..."
	$(VENV_PIP) install --upgrade pip
	$(VENV_PIP) install -r requirements.txt
	@echo "Installing package in development mode..."
	$(VENV_PIP) install -e .

# Install dependencies only
.PHONY: install
install: $(VENV_NAME)
	$(VENV_PIP) install -r requirements.txt

# Install in development mode
.PHONY: dev
dev: $(VENV_NAME)
	$(VENV_PIP) install -e .

# Run the server
.PHONY: run
run: $(VENV_NAME)
	@if [ ! -f .env ]; then \
		echo "Warning: .env file not found. Copying from .env.example..."; \
		cp .env.example .env; \
		echo "Please edit .env and add your ETHERSCAN_API_KEY"; \
		exit 1; \
	fi
	@echo "Starting MCP Etherscan Server..."
	$(VENV_PYTHON) -m mcp_etherscan_server.main

# Quick start (setup + run)
.PHONY: start
start: setup
	@echo "Starting server after setup..."
	@$(MAKE) run

# Test the installation
.PHONY: test
test: $(VENV_NAME)
	@echo "Testing installation..."
	$(VENV_PYTHON) -c "import mcp_etherscan_server; print('Package imports successfully')"
	@echo "Checking dependencies..."
	$(VENV_PIP) check

# Lint code
.PHONY: lint
lint: $(VENV_NAME)
	@echo "Linting code..."
	$(VENV_PYTHON) -m flake8 src/ --max-line-length=100 --ignore=E501,W503 || echo "Install flake8: $(VENV_PIP) install flake8"

# Show environment information
.PHONY: env
env: $(VENV_NAME)
	@echo "Environment Information:"
	@echo "Python: $(shell $(VENV_PYTHON) --version)"
	@echo "Pip: $(shell $(VENV_PIP) --version)"
	@echo "Virtual env: $(VENV_NAME)"
	@echo "Installed packages:"
	@$(VENV_PIP) list

# Clean up
.PHONY: clean
clean:
	@echo "Cleaning up..."
	rm -rf $(VENV_NAME)
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	@echo "Cleanup complete"

# Force reinstall
.PHONY: reinstall
reinstall: clean setup

# Check if API key is configured
.PHONY: check-env
check-env:
	@if [ ! -f .env ]; then \
		echo "ERROR: .env file not found. Run 'cp .env.example .env' and configure it"; \
		exit 1; \
	fi
	@if ! grep -q "ETHERSCAN_API_KEY=.*[^=]" .env; then \
		echo "ERROR: ETHERSCAN_API_KEY not configured in .env file"; \
		exit 1; \
	fi
	@echo "Environment configuration looks good"