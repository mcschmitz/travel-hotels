# Hotel Search API Documentation

## Overview

The Hotel Search API provides access to hotel search functionality powered by SearchAPI.io's Google Hotels integration. This API allows you to search for hotels by location, dates, and various parameters.

## Base URL

```
http://localhost:8000 (development)
```

## Authentication

The API requires a SearchAPI.io API key to be configured via environment variable:

```bash
SEARCHAPI_API_KEY=your_searchapi_key_here
```

## Endpoints

### GET /api/v1/hotels/search

Search for hotels by location and date range.

#### Parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `q` | string | Yes | Location query (1-200 characters) | "New York" |
| `check_in` | string | Yes | Check-in date (YYYY-MM-DD, must be today or future) | "2024-12-01" |
| `check_out` | string | Yes | Check-out date (YYYY-MM-DD, must be after check-in) | "2024-12-05" |
| `adults` | integer | No | Number of adults (1-10, default: 2) | 2 |
| `property_type` | string | No | Type of property (default: "hotel") | "hotel" |

#### Property Types

- `hotel` - Traditional hotels
- `vacation_rental` - Vacation rentals and apartments
- `bed_and_breakfast` - B&Bs and guesthouses
- `resort` - Resort properties
- `hostel` - Hostels and budget accommodations

#### Example Request

```bash
curl "http://localhost:8000/api/v1/hotels/search?q=New%20York&check_in=2024-12-01&check_out=2024-12-05&adults=2&property_type=hotel"
```

#### Example Response

```json
{
  "search_metadata": {
    "id": "search_123456",
    "status": "Success",
    "json_endpoint": "https://serpapi.com/searches/...",
    "created_at": "2024-09-21T20:00:00Z",
    "processed_at": "2024-09-21T20:00:02Z",
    "google_hotels_url": "https://www.google.com/travel/hotels/...",
    "raw_html_file": "https://serpapi.com/searches/..."
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
      "link": "https://www.google.com/travel/hotels/...",
      "gps_coordinates": {
        "latitude": 40.764749,
        "longitude": -73.974663
      },
      "check_in_time": "3:00 PM",
      "check_out_time": "12:00 PM",
      "rate_per_night": {
        "lowest": "$450",
        "extracted_lowest": 450,
        "before_taxes_fees": "$420",
        "extracted_before_taxes_fees": 420
      },
      "total_rate": {
        "lowest": "$1800",
        "extracted_lowest": 1800,
        "before_taxes_fees": "$1680",
        "extracted_before_taxes_fees": 1680
      },
      "nearby_places": [
        {
          "name": "Central Park",
          "transportations": [
            {
              "type": "Walking",
              "duration": "2 min"
            }
          ]
        }
      ],
      "amenities": [
        "Free WiFi",
        "Fitness center",
        "Restaurant",
        "Room service"
      ],
      "excluded_amenities": [
        "Free parking"
      ],
      "essential_info": [
        "Non-smoking",
        "Air conditioning"
      ]
    }
  ]
}
```

#### Response Fields

##### search_metadata
- `id` - Unique search identifier
- `status` - Search status ("Success", "Error")
- `created_at` - When the search was initiated
- `processed_at` - When the search was completed
- `google_hotels_url` - Direct Google Hotels URL
- `json_endpoint` - API endpoint for this search
- `raw_html_file` - Raw HTML response (if available)

##### search_parameters
- `q` - Search location query
- `check_in` - Check-in date
- `check_out` - Check-out date
- `adults` - Number of adults
- `property_type` - Property type filter

##### properties
Array of hotel properties with details:
- `name` - Hotel name
- `description` - Hotel description
- `link` - Direct booking link
- `gps_coordinates` - Latitude and longitude
- `check_in_time` - Check-in time
- `check_out_time` - Check-out time
- `rate_per_night` - Nightly rate information
- `total_rate` - Total stay cost
- `nearby_places` - Nearby attractions and distances
- `amenities` - Available amenities
- `excluded_amenities` - Not available amenities
- `essential_info` - Important property information

## Error Responses

The API returns appropriate HTTP status codes and error messages:

### 400 Bad Request
Invalid request parameters.

```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["query", "q"],
      "msg": "String should have at least 1 character",
      "input": "",
      "ctx": {"min_length": 1}
    }
  ]
}
```

### 401 Unauthorized
Invalid or missing SearchAPI.io API key.

```json
{
  "detail": "SearchAPI.io authentication failed. Please check your API key."
}
```

### 422 Unprocessable Entity
Validation errors (e.g., invalid dates, check-in date in the past).

```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["query", "check_in"],
      "msg": "Check-in date must be today or in the future",
      "input": "2023-01-01"
    }
  ]
}
```

### 429 Too Many Requests
Rate limit exceeded.

```json
{
  "detail": "Rate limit exceeded. Please try again later."
}
```

### 502 Bad Gateway
SearchAPI.io service error.

```json
{
  "detail": "External service error. Please try again later."
}
```

### 504 Gateway Timeout
SearchAPI.io request timeout.

```json
{
  "detail": "Search request timed out. Please try again."
}
```

### 500 Internal Server Error
Unexpected server error.

```json
{
  "detail": "An unexpected error occurred. Please contact support."
}
```

## Rate Limits

- SearchAPI.io has rate limits that vary by plan
- The API handles rate limiting gracefully and returns 429 status codes
- Implement exponential backoff for retries

## Performance

- Typical response time: 2-8 seconds
- Maximum response time: 15 seconds
- Responses are not cached - each request queries SearchAPI.io in real-time

## Best Practices

1. **Input Validation**: Always validate dates and parameters client-side
2. **Error Handling**: Implement proper error handling for all status codes
3. **Rate Limiting**: Respect rate limits and implement retry logic
4. **Timeout Handling**: Set appropriate timeouts (15+ seconds recommended)
5. **Location Specificity**: Use specific location queries for better results
6. **Date Validation**: Ensure check-in dates are in the future and check-out is after check-in

## Examples

### Basic Hotel Search
```bash
curl "http://localhost:8000/api/v1/hotels/search?q=Paris&check_in=2024-12-01&check_out=2024-12-05"
```

### Search with All Parameters
```bash
curl "http://localhost:8000/api/v1/hotels/search?q=Tokyo%20Japan&check_in=2024-12-15&check_out=2024-12-20&adults=4&property_type=hotel"
```

### Vacation Rental Search
```bash
curl "http://localhost:8000/api/v1/hotels/search?q=San%20Francisco&check_in=2024-11-01&check_out=2024-11-07&adults=2&property_type=vacation_rental"
```

## Testing

Use the integration test suite to validate API functionality:

```bash
# Set your API key
export SEARCHAPI_API_KEY=your_key_here

# Run integration tests
uv run python -m pytest tests/integration/ -v

# Run performance tests
uv run python -m pytest tests/integration/ -v -m slow
```

## OpenAPI Documentation

Interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
