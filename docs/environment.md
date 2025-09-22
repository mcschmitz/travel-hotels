# Environment Setup Guide

## Overview

This guide provides detailed instructions for setting up the Hotel Search API development and production environments.

## Prerequisites

### System Requirements

- **Python**: 3.11 or higher
- **Package Manager**: uv (recommended) or pip
- **Git**: For version control
- **Docker**: Optional, for containerized development
- **SearchAPI.io Account**: Required for API access

### Platform Support

- **Linux**: Ubuntu 20.04+, CentOS 8+
- **macOS**: 10.15 (Catalina) or higher
- **Windows**: Windows 10/11 with WSL2 recommended

## SearchAPI.io Setup

### 1. Create SearchAPI.io Account

1. Visit [SearchAPI.io](https://serpapi.com/)
2. Sign up for an account
3. Choose an appropriate plan for your usage needs
4. Obtain your API key from the dashboard

### 2. API Key Configuration

Your API key will be used to authenticate requests to Google Hotels API.

**Free Plan Limits:**
- 100 searches per month
- Rate limited

**Paid Plans:**
- Higher search limits
- Better rate limits
- Priority support

## Development Environment Setup

### Option 1: Using uv (Recommended)

#### 1. Install uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Alternative: using pip
pip install uv
```

#### 2. Project Setup

```bash
# Clone repository
git clone <repository-url>
cd travel-hotels

# Create virtual environment and install dependencies
uv install

# Activate virtual environment (if needed)
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate     # Windows
```

#### 3. Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env file
nano .env
```

**.env file content:**
```bash
# SearchAPI.io Configuration
SEARCHAPI_API_KEY=your_searchapi_key_here

# Development Configuration
APP_NAME=Hotel Search API
VERSION=1.0.0
DEBUG=true
HOST=localhost
PORT=8000

# Optional: CORS for development
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

#### 4. Verify Installation

```bash
# Run development server
uv run python src/main.py

# Or use uvicorn
uv run uvicorn src.main:create_app --host localhost --port 8000 --reload

# Test API
curl http://localhost:8000/health
```

### Option 2: Using pip/venv

#### 1. Create Virtual Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate     # Windows
```

#### 2. Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Or install from pyproject.toml
pip install -e .
```

#### 3. Configuration and Testing

Follow steps 3-4 from the uv option above.

### Option 3: Using Docker

#### 1. Docker Development Setup

```bash
# Build development image
docker build -t hotel-search-api-dev .

# Run with environment file
docker run -d \
  --name hotel-search-api-dev \
  -p 8000:8000 \
  --env-file .env \
  -v $(pwd)/src:/app/src \
  hotel-search-api-dev

# Or use docker-compose
docker-compose up -d
```

#### 2. Docker Compose Configuration

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - SEARCHAPI_API_KEY=${SEARCHAPI_API_KEY}
      - DEBUG=true
    volumes:
      - ./src:/app/src
    restart: unless-stopped

  # Optional: Add nginx for load balancing
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - api
```

## IDE and Editor Setup

### Visual Studio Code

#### Recommended Extensions

```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.black-formatter",
    "ms-python.isort",
    "ms-python.mypy-type-checker",
    "charliermarsh.ruff",
    "ms-python.pytest",
    "ms-vscode.vscode-typescript-next"
  ]
}
```

#### Settings Configuration

**.vscode/settings.json:**
```json
{
  "python.defaultInterpreterPath": ".venv/bin/python",
  "python.terminal.activateEnvironment": true,
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["tests"],
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "python.formatting.provider": "black",
  "python.sortImports.args": ["--profile", "black"],
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  }
}
```

### PyCharm

1. Open project in PyCharm
2. Configure Python interpreter: `.venv/bin/python`
3. Enable pytest as test runner
4. Configure code style: Black formatter
5. Enable type checking: mypy

## Environment Variables Reference

### Core Configuration

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `SEARCHAPI_API_KEY` | SearchAPI.io API key | None | `abc123def456...` |
| `APP_NAME` | Application name | "Hotel Search API" | "My Hotel API" |
| `VERSION` | API version | "1.0.0" | "2.1.0" |
| `DEBUG` | Debug mode | false | true/false |
| `HOST` | Host to bind | "0.0.0.0" | "localhost" |
| `PORT` | Port to bind | 8000 | 8080 |

### Optional Configuration

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `CORS_ORIGINS` | Allowed CORS origins | None | "http://localhost:3000" |
| `LOG_LEVEL` | Logging level | "INFO" | "DEBUG" |
| `WORKERS` | Number of workers | 1 | 4 |

### SearchAPI.io Configuration

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `SEARCHAPI_BASE_URL` | SearchAPI base URL | serpapi.com | custom.domain.com |
| `SEARCHAPI_TIMEOUT` | Request timeout | 30 | 60 |
| `SEARCHAPI_RETRIES` | Max retries | 3 | 5 |

## Development Tools

### Code Quality Tools

```bash
# Linting with ruff
uv run ruff check src/ tests/

# Type checking with mypy
uv run mypy src/

# Security scanning with bandit
uv run bandit -r src/

# Code formatting with ruff
uv run ruff format src/ tests/
```

### Testing

```bash
# Run all tests
uv run python -m pytest

# Run with coverage
uv run python -m pytest --cov=src

# Run integration tests (requires API key)
export SEARCHAPI_API_KEY=your_key
uv run python -m pytest tests/integration/

# Run specific test file
uv run python -m pytest tests/app/test_hotel_service.py -v
```

### Development Scripts

Create useful development scripts:

**scripts/dev.sh:**
```bash
#!/bin/bash
export DEBUG=true
export SEARCHAPI_API_KEY=${SEARCHAPI_API_KEY:-"your_dev_key"}
uv run uvicorn src.main:create_app --host localhost --port 8000 --reload
```

**scripts/test.sh:**
```bash
#!/bin/bash
uv run python -m pytest tests/ --cov=src --cov-report=html
```

**scripts/lint.sh:**
```bash
#!/bin/bash
uv run ruff check src/ tests/
uv run mypy src/
uv run bandit -r src/
```

## Production Environment Setup

### 1. Server Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11
sudo apt install python3.11 python3.11-venv python3.11-dev

# Install system dependencies
sudo apt install curl git nginx supervisor

# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Application Deployment

```bash
# Create application user
sudo useradd -m -s /bin/bash hotelapi

# Clone repository
sudo -u hotelapi git clone <repo> /home/hotelapi/app
cd /home/hotelapi/app

# Install dependencies
sudo -u hotelapi uv install --no-dev

# Set up environment
sudo -u hotelapi cp .env.prod.example .env.prod
sudo -u hotelapi nano .env.prod
```

### 3. Process Management

**Supervisor Configuration (/etc/supervisor/conf.d/hotelapi.conf):**
```ini
[program:hotelapi]
command=/home/hotelapi/app/.venv/bin/uvicorn src.main:create_app --host 0.0.0.0 --port 8000
directory=/home/hotelapi/app
user=hotelapi
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/hotelapi.log
environment=PATH="/home/hotelapi/app/.venv/bin",SEARCHAPI_API_KEY="your_prod_key"
```

```bash
# Reload supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start hotelapi
```

## Environment Validation

### Health Check Script

**scripts/health_check.py:**
```python
#!/usr/bin/env python3
import os
import sys
import requests
from urllib.parse import urljoin

def check_environment():
    """Validate environment setup."""
    errors = []

    # Check API key
    api_key = os.getenv('SEARCHAPI_API_KEY')
    if not api_key:
        errors.append("SEARCHAPI_API_KEY not set")

    # Check API endpoint
    try:
        response = requests.get('http://localhost:8000/health', timeout=5)
        if response.status_code != 200:
            errors.append(f"Health check failed: {response.status_code}")
    except requests.RequestException as e:
        errors.append(f"Cannot connect to API: {e}")

    # Check SearchAPI.io connectivity
    if api_key:
        try:
            response = requests.get(
                'https://serpapi.com/search.json',
                params={'engine': 'google_hotels', 'q': 'test', 'api_key': api_key},
                timeout=10
            )
            if response.status_code != 200:
                errors.append(f"SearchAPI.io test failed: {response.status_code}")
        except requests.RequestException as e:
            errors.append(f"SearchAPI.io connectivity issue: {e}")

    if errors:
        print("❌ Environment validation failed:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    else:
        print("✅ Environment validation passed")

if __name__ == "__main__":
    check_environment()
```

Run validation:
```bash
uv run python scripts/health_check.py
```

## Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Check Python path
   python -c "import sys; print(sys.path)"

   # Reinstall dependencies
   uv install --refresh
   ```

2. **API Key Issues**
   ```bash
   # Verify API key is set
   echo $SEARCHAPI_API_KEY

   # Test API key directly
   curl "https://serpapi.com/search.json?engine=google_hotels&q=test&api_key=$SEARCHAPI_API_KEY"
   ```

3. **Port Conflicts**
   ```bash
   # Check what's using port 8000
   lsof -i :8000

   # Use different port
   uv run uvicorn src.main:create_app --port 8001
   ```

4. **Permission Issues**
   ```bash
   # Fix file permissions
   chmod +x scripts/*.sh

   # Fix virtual environment permissions
   chmod -R 755 .venv/
   ```

### Debug Mode

Enable debug mode for detailed error information:

```bash
export DEBUG=true
uv run python src/main.py
```

### Logging Configuration

Configure logging for debugging:

```python
import logging
from loguru import logger

# Enable debug logging
logger.remove()
logger.add(sys.stderr, level="DEBUG")
```
