# 🏨 Travel Hotels API

A FastAPI-based microservice for hotel search powered by SearchAPI.io's Google Hotels integration. This service provides comprehensive hotel search functionality with real-time data, robust error handling, and production-ready architecture.

## ✨ Features

- **🔍 Hotel Search**: Search hotels by location, dates, and preferences
- **📍 Global Coverage**: Powered by Google Hotels via SearchAPI.io
- **⚡ Real-time Data**: Live hotel availability and pricing
- **🛡️ Robust Error Handling**: Comprehensive error scenarios with proper HTTP status codes
- **🏭 Production Ready**: Factory pattern, lifecycle management, and comprehensive testing

## 🏗️ Architecture

### ⚙️ Core Components

- **FastAPI**: Modern, fast web framework with automatic OpenAPI documentation
- **SearchAPI.io Integration**: Google Hotels API access with rate limiting and error handling
- **Async HTTP Client**: HTTPX-based client with proper lifecycle management
- **Factory Pattern**: Dependency injection and service lifecycle management
- **Comprehensive Testing**: Unit, integration, and end-to-end test coverage
- **Pydantic Validation**: Strong typing and data validation throughout

### 🧱 Service Architecture

```
FastAPI Router → Hotel Controller → Hotel Service → SearchAPI Client → Google Hotels API
```

## 🚀 Quick Start

### 📋 Prerequisites

- Python 3.12+
- UV package manager
- Docker and Docker Compose
- SearchAPI.io API key

### ⚡ Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd travel-hotels
   ```

2. **Install dependencies**

   ```bash
   uv install
   ```

3. **Set up environment variables**

   ```bash
   cp .env.example .env
   # Edit .env with your SearchAPI.io API key
   SEARCHAPI_API_KEY=your_searchapi_key_here
   ```

4. **Start the development server**

   ```bash
   # Using uv
   uv run python src/main.py

   # Or using Docker
   poe serve
   ```

5. **Verify installation**

   ```bash
   # Health check
   curl http://localhost:8000/health

   # API documentation
   open http://localhost:8000/docs
   ```

## 💻 Development

### 🛠️ Available Commands

```bash
# Testing
poe test                    # Run test suite with coverage
uv run python -m pytest    # Run tests directly

# Code Quality
poe lint                    # Run ruff linting
poe format                  # Format code with ruff
poe check-mypy             # Type checking with mypy
poe check-bandit           # Security vulnerability scan

# Docker Operations
poe build                   # Build Docker container
poe serve                   # Start application with docker-compose

# Database Operations
uv run alembic upgrade head              # Apply migrations
uv run alembic revision --autogenerate  # Create new migration
```

### 📁 Project Structure

```
src/
├── api/                    # FastAPI routers and endpoints
│   ├── dependencies/       # Dependency injection
│   └── hotels.py          # Hotel search endpoint
├── app/                   # Core business logic
│   ├── controllers/       # Request/response handling
│   └── schemas/           # Pydantic models for validation
├── core/                  # Infrastructure and configuration
│   └── config.py         # Settings and configuration
└── main.py               # Application entry point
tests/
├── integration/          # End-to-end integration tests
├── untittests/          # Unit tests by component
└── conftest.py          # Test configuration and fixtures
```

### 🧪 Testing Strategy

The project uses pytest with a comprehensive testing approach:

- **Unit Tests**: Test individual components in isolation with proper mocking
- **Integration Tests**: End-to-end API testing with real HTTP requests

### 🔐 Authentication

## 🌐 API Endpoints

### 🏨 Hotel Search

**GET `/api/v1/hotels/search`**

Search for hotels by location and date range.

```bash
# Basic search
curl "http://localhost:8000/api/v1/hotels/search?q=New%20York&check_in=2024-12-01&check_out=2024-12-05"

# Advanced search
curl "http://localhost:8000/api/v1/hotels/search?q=Paris&check_in=2024-12-01&check_out=2024-12-05&adults=2&property_type=hotel"
```

**Parameters:**

- `q` (required): Location query (e.g., "New York", "Paris, France")
- `check_in` (required): Check-in date (YYYY-MM-DD, must be today or future)
- `check_out` (required): Check-out date (YYYY-MM-DD, must be after check-in)
- `adults` (optional): Number of adults (1-10, default: 2)
- `property_type` (optional): Property type (hotel, vacation_rental, bed_and_breakfast, resort, hostel)

**Response:**

```json
{
  "search_metadata": {
    "id": "search_123456",
    "status": "Success",
    "created_at": "2024-09-21T20:00:00Z",
    "processed_at": "2024-09-21T20:00:02Z"
  },
  "search_parameters": {
    "q": "New York",
    "check_in": "2024-12-01",
    "check_out": "2024-12-05",
    "adults": 2,
    "property_type": "hotel"
  },
  "properties": [
    {
      "name": "The Plaza Hotel",
      "description": "Luxury hotel in Manhattan",
      "rate_per_night": {
        "lowest": "$450",
        "extracted_lowest": 450
      },
      "total_rate": {
        "lowest": "$1800",
        "extracted_lowest": 1800
      },
      "gps_coordinates": {
        "latitude": 40.764749,
        "longitude": -73.974663
      },
      "amenities": ["Free WiFi", "Fitness center", "Restaurant"],
      "nearby_places": [
        {
          "name": "Central Park",
          "transportations": [{"type": "Walking", "duration": "2 min"}]
        }
      ]
    }
  ]
}
```

### 📊 Health Check

**GET `/health`**

Basic health check endpoint.

```bash
curl http://localhost:8000/health
# Response: {"status": "healthy"}
```

### 📚 API Documentation

- **Swagger UI**: <http://localhost:8000/docs>
- **ReDoc**: <http://localhost:8000/redoc>
- **OpenAPI Schema**: <http://localhost:8000/openapi.json>

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `SEARCHAPI_API_KEY` | SearchAPI.io API key | Yes | None |
| `APP_NAME` | Application name | No | "Hotel Search API" |
| `VERSION` | API version | No | "1.0.0" |
| `DEBUG` | Debug mode | No | false |
| `HOST` | Host to bind to | No | "0.0.0.0" |
| `PORT` | Port to bind to | No | 8000 |
| `CORS_ORIGINS` | Allowed CORS origins | No | None |

### SearchAPI.io Setup

1. Sign up at SearchAPI.io
2. Get your API key from the dashboard
3. Set the `SEARCHAPI_API_KEY` environment variable
4. Choose an appropriate plan for your usage needs

## 🧪 Testing

### Test Suite

```bash
# Run all tests
uv run python -m pytest

# Run with coverage
uv run python -m pytest --cov=src --cov-report=html

# Run integration tests (requires API key)
export SEARCHAPI_API_KEY=your_key
uv run python -m pytest tests/integration/ -v

# Run performance tests
uv run python -m pytest tests/integration/ -v -m slow
```

### Test Types

- **Unit Tests**: Individual component testing with mocking
- **Integration Tests**: End-to-end API testing with real SearchAPI.io calls

## 🚢 Deployment

### Cloud Deployment

## 🛡️ Error Handling

The API provides comprehensive error handling with appropriate HTTP status codes:

- **400 Bad Request**: Invalid parameters
- **401 Unauthorized**: Invalid API key
- **422 Unprocessable Entity**: Validation errors
- **429 Too Many Requests**: Rate limit exceeded
- **502 Bad Gateway**: SearchAPI.io service error
- **504 Gateway Timeout**: Request timeout
- **500 Internal Server Error**: Unexpected errors

## 🔧 Development Tools

### Code Quality

```bash
# Linting and formatting
poe lint                    # Run ruff linting
poe format                  # Format code with ruff
poe check-mypy             # Type checking with mypy
poe check-bandit           # Security vulnerability scan

# All quality checks
poe lint && poe check-mypy && poe check-bandit
```
