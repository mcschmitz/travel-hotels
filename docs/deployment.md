# Hotel Search API Deployment Guide

## Overview

This guide covers deploying the Hotel Search API to production environments. The API is built with FastAPI and requires SearchAPI.io integration.

## Prerequisites

- Python 3.11+ with uv package manager
- SearchAPI.io API key
- Docker (for containerized deployment)
- Production server or cloud platform

## Environment Variables

### Required Environment Variables

```bash
# SearchAPI.io Configuration
SEARCHAPI_API_KEY=your_searchapi_key_here

# Server Configuration
APP_NAME="Hotel Search API"
VERSION="1.0.0"
DEBUG=false
HOST=0.0.0.0
PORT=8000

# Optional: CORS Configuration
CORS_ORIGINS="https://yourdomain.com,https://app.yourdomain.com"
```

### Environment Variable Details

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `SEARCHAPI_API_KEY` | SearchAPI.io API key | None | Yes |
| `APP_NAME` | Application name | "Hotel Search API" | No |
| `VERSION` | API version | "1.0.0" | No |
| `DEBUG` | Debug mode | false | No |
| `HOST` | Host to bind to | "0.0.0.0" | No |
| `PORT` | Port to bind to | 8000 | No |
| `CORS_ORIGINS` | Allowed CORS origins | None | No |

## Local Development Setup

### 1. Clone and Setup

```bash
git clone <repository-url>
cd travel-hotels
```

### 2. Install Dependencies

```bash
# Using uv (recommended)
uv install

# Or using pip
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Create .env file
cp .env.example .env

# Edit .env with your configuration
SEARCHAPI_API_KEY=your_key_here
DEBUG=true
```

### 4. Run Development Server

```bash
# Using uv
uv run python src/main.py

# Or using uvicorn directly
uvicorn src.main:create_app --host localhost --port 8000 --reload
```

### 5. Verify Installation

```bash
# Health check
curl http://localhost:8000/health

# API documentation
open http://localhost:8000/docs
```

## Docker Deployment

### 1. Build Docker Image

```bash
# Build image
docker build -t hotel-search-api .

# Or using docker-compose
docker-compose build
```

### 2. Run with Docker

```bash
# Run single container
docker run -d \
  --name hotel-search-api \
  -p 8000:8000 \
  -e SEARCHAPI_API_KEY=your_key_here \
  -e DEBUG=false \
  hotel-search-api

# Or using docker-compose
docker-compose up -d
```

### 3. Docker Environment File

Create `.env.prod` for production:

```bash
SEARCHAPI_API_KEY=your_production_key
APP_NAME=Hotel Search API
VERSION=1.0.0
DEBUG=false
HOST=0.0.0.0
PORT=8000
```

Run with environment file:

```bash
docker run -d \
  --name hotel-search-api \
  -p 8000:8000 \
  --env-file .env.prod \
  hotel-search-api
```

## Cloud Platform Deployment

### AWS ECS Deployment

1. **Create Task Definition**

```json
{
  "family": "hotel-search-api",
  "taskRoleArn": "arn:aws:iam::account:role/ecsTaskRole",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "containerDefinitions": [
    {
      "name": "hotel-search-api",
      "image": "your-account.dkr.ecr.region.amazonaws.com/hotel-search-api:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "SEARCHAPI_API_KEY",
          "value": "your_key_here"
        },
        {
          "name": "DEBUG",
          "value": "false"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/hotel-search-api",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

2. **Create ECS Service**

```bash
aws ecs create-service \
  --cluster production \
  --service-name hotel-search-api \
  --task-definition hotel-search-api:1 \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-12345],securityGroups=[sg-12345],assignPublicIp=ENABLED}"
```

### Google Cloud Run Deployment

```bash
# Build and push to Google Container Registry
gcloud builds submit --tag gcr.io/project-id/hotel-search-api

# Deploy to Cloud Run
gcloud run deploy hotel-search-api \
  --image gcr.io/project-id/hotel-search-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars SEARCHAPI_API_KEY=your_key_here,DEBUG=false
```

### Azure Container Instances

```bash
# Create container instance
az container create \
  --resource-group myResourceGroup \
  --name hotel-search-api \
  --image your-registry.azurecr.io/hotel-search-api:latest \
  --cpu 1 \
  --memory 1 \
  --ports 8000 \
  --environment-variables SEARCHAPI_API_KEY=your_key_here DEBUG=false
```

## Production Configuration

### 1. Security Considerations

- **HTTPS Only**: Always use HTTPS in production
- **API Key Security**: Store API keys securely (AWS Secrets Manager, etc.)
- **CORS Configuration**: Configure allowed origins appropriately
- **Rate Limiting**: Implement API rate limiting
- **Input Validation**: All inputs are validated by FastAPI/Pydantic

### 2. Performance Optimization

```python
# Dockerfile optimization
FROM python:3.11-slim

# Install dependencies first (better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ src/

# Use gunicorn for production
CMD ["gunicorn", "src.main:create_app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

### 3. Health Checks

Configure health checks for your deployment:

```bash
# Health check endpoint
curl http://your-api/health

# Expected response
{"status": "healthy"}
```

### 4. Monitoring and Logging

- **Application Logs**: Structured logging with loguru
- **Metrics**: Monitor response times, error rates
- **Alerts**: Set up alerts for failures and performance issues

## Load Balancer Configuration

### Nginx Configuration

```nginx
upstream hotel_search_api {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
}

server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://hotel_search_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Increase timeout for SearchAPI calls
        proxy_read_timeout 30s;
        proxy_connect_timeout 10s;
    }
}
```

## Scaling Considerations

### Horizontal Scaling

- **Stateless Design**: API is stateless and scales horizontally
- **Load Balancing**: Use load balancer to distribute requests
- **Auto Scaling**: Configure auto-scaling based on CPU/memory usage

### Rate Limiting

SearchAPI.io has rate limits - consider:

- **Request Queuing**: Queue requests during high load
- **Caching**: Cache frequent searches (with TTL)
- **Rate Limit Headers**: Respect SearchAPI.io rate limit headers

## Troubleshooting

### Common Issues

1. **SearchAPI.io Authentication Errors**
   ```bash
   # Check API key
   echo $SEARCHAPI_API_KEY

   # Test API key directly
   curl "https://serpapi.com/search.json?engine=google_hotels&q=New+York&api_key=$SEARCHAPI_API_KEY"
   ```

2. **Timeout Issues**
   - Increase proxy timeouts
   - Check SearchAPI.io service status
   - Monitor response times

3. **Memory Issues**
   - Monitor memory usage
   - Increase container memory limits
   - Check for memory leaks

### Log Analysis

```bash
# Check application logs
docker logs hotel-search-api

# Search for errors
docker logs hotel-search-api 2>&1 | grep ERROR

# Monitor real-time logs
docker logs -f hotel-search-api
```

## Backup and Recovery

- **Stateless Application**: No data to backup
- **Configuration**: Backup environment variables and deployment configs
- **Monitoring**: Monitor API availability and performance

## Security Checklist

- [ ] HTTPS enforced
- [ ] API keys stored securely
- [ ] CORS properly configured
- [ ] Rate limiting implemented
- [ ] Input validation enabled
- [ ] Security headers configured
- [ ] Container security scanned
- [ ] Network security configured
