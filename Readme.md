# 🌍 Travel Hotels

The Travel Hotels Service is a FastAPI-based microservice that allows the client to get hotel information.

## 🏗️ Architecture

### ⚙️ Core Components

- **FastAPI**: Modern, fast web framework for building APIs
- **Async HTTP Client**: HTTPX-based client with proper lifecycle management
- **Comprehensive Error Handling**: Custom exceptions for different API failure scenarios

## 🚀 Quick Start

### 📋 Prerequisites

- Python 3.12+
- UV package manager
- Docker and Docker Compose

### ⚡ Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd travel-activities
   ```

2. **Install dependencies**

   ```bash
   uv sync
   ```

3. **Set up environment variables**

   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Start with Docker**

   ```bash
   poe serve
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

### 🧪 Testing Strategy

The project uses pytest with a comprehensive testing approach:

- **Unit Tests**: Test individual components in isolation with proper mocking
- **Integration Tests**: End-to-end API testing with real HTTP requests
- **Parametrized Tests**: Efficient testing of multiple scenarios
- **Coverage Reporting**: Maintains high test coverage (90%+)
- **Async Testing**: Proper async/await patterns for all async code

### 🔐 Authentication

## 🌐 API Endpoints

### 🎯 Activity Search

## ⚙️ Configuration

### Environment Variables

## 🗄️ Database Schema

### ✅ Code Quality Rules

## 🚀 Production Deployment

## 📊 Monitoring and Observability

## 📄 License
