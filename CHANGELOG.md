# Changelog

## 0.1.0 - 2025-09-22

### ✨ Features

- **Hotel Search API**:
  - GET `/api/v1/hotels/search` endpoint with comprehensive query parameter validation
  - Support for location search, date ranges, adult counts, and property types
  - Real-time hotel availability and pricing data
  - Global coverage powered by Google Hotels API

### 🏗️ Architecture

- **Factory Pattern**:
  - `ServiceFactory` for external service management
  - `ControllerFactory` for HTTP request handling
  - Singleton pattern implementation with proper cleanup
- **Async Architecture**: Full async/await implementation throughout the stack
  - HTTPX-based HTTP client with connection pooling
  - FastAPI async endpoints and middleware
  - Proper resource lifecycle management

### 🧪 Testing

- **Comprehensive Test Suite**:
  - Unit tests for all service components with proper mocking
  - Integration tests for API endpoints with FastAPI TestClient
  - End-to-end tests with real SearchAPI.io API calls
  - Performance benchmarking and validation tests

## 0.0.1 - 2025-09-19

### ✨ Features

- Add initial FastAPI application structure with health check and root endpoints
- Add hotels API router endpoint configuration
- Add core configuration management using Pydantic settings
- Add application metadata retrieval from pyproject.toml

### 🏗️ Infrastructure

- Add comprehensive GitHub Actions CI/CD workflow for linting, testing, and security checks
- Add pull request template with categorized change types
- Add pre-commit hooks for code quality (ruff, mypy, bandit)
- Add Docker configuration with multi-stage build using uv
- Add docker-compose.yml for local development
- Add comprehensive .gitignore for Python projects
- Set Python version to 3.12

### 🧪 Testing

- Add initial test structure with unittest and services test directories
- Add pytest configuration for test execution

### 🔒 Security

- Add bandit security vulnerability scanning
- Add comprehensive security checks in CI pipeline
