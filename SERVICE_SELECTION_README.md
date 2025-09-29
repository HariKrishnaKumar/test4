# Service Selection API

This document describes the Service Selection API endpoints that allow users to select or speak their preferred service type.

## Overview

The Service Selection API provides two main input methods:
1. **Text Input**: Direct service selection via text
2. **Voice Input**: AI-powered service detection from voice text

## Features

- ✅ Text-based service selection
- ✅ Voice-based service detection using AI (Gemini)
- ✅ Multiple service detection from single input
- ✅ User-based service storage
- ✅ Service validation
- ✅ Available services management
- ✅ Service detection testing endpoint
- ✅ User service history tracking

## Database Schema

### Services Table
```sql
CREATE TABLE services (
    id INT PRIMARY KEY AUTO_INCREMENT,
    service_name VARCHAR(100) NOT NULL UNIQUE,
    service_description VARCHAR(255),
    is_active VARCHAR(10) DEFAULT 'true',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME ON UPDATE CURRENT_TIMESTAMP
);
```

### User Services Table
```sql
CREATE TABLE user_services (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    service_id INT NOT NULL,
    selected_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (service_id) REFERENCES services(id)
);
```

## Available Services

The system comes with 5 default services:

1. **Delivery** - Home delivery service
2. **Pickup** - Self-pickup service
3. **Reservation** - Table reservation service
4. **Catering** - Catering service for events
5. **Events** - Event planning service

## API Endpoints

### 1. Select Service
**POST** `/service/select`

Select or detect service from text or voice input.

**Request Body:**
```json
{
    "user_id": "integer",
    "service_text": "string",
    "input_type": "text|voice"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Service 'Delivery' selected successfully",
    "selected_service": "Delivery",
    "user_id": 1,
    "detected_services": ["Delivery"],
    "service_id": 1
}
```

### 2. Get User Services
**GET** `/service/user/{user_id}`

Get all services selected by a user.

**Response:**
```json
{
    "success": true,
    "user_id": 1,
    "services": [
        {
            "id": 1,
            "user_id": 1,
            "service_id": 1,
            "service_name": "Delivery",
            "selected_at": "2025-09-12T14:26:12.896346"
        }
    ],
    "total_services": 1
}
```

### 3. Get Available Services
**GET** `/service/available`

Get list of all available services.

**Response:**
```json
[
    {
        "id": 1,
        "service_name": "Delivery",
        "service_description": "Home delivery service - bringing food to your address",
        "is_active": "true",
        "created_at": "2025-09-12T14:26:12.896346",
        "updated_at": null
    }
]
```

### 4. Add Service
**POST** `/service/available`

Add a new service to the available services list.

**Request Body:**
```json
{
    "service_name": "string",
    "service_description": "string (optional)"
}
```

### 5. Detect Services (Testing)
**POST** `/service/detect`

Detect services from text using AI (for testing/debugging).

**Query Parameters:**
- `text`: The text to analyze

**Response:**
```json
{
    "success": true,
    "input_text": "I want delivery at my house",
    "detected_services": ["Delivery"],
    "primary_service": "Delivery"
}
```

### 6. Get Latest User Service
**GET** `/service/user/{user_id}/latest`

Get the most recently selected service for a user.

**Response:**
```json
{
    "success": true,
    "user_id": 1,
    "service": {
        "id": 1,
        "service_id": 1,
        "service_name": "Delivery",
        "selected_at": "2025-09-12T14:26:12.896346"
    }
}
```

### 7. Remove User Service
**DELETE** `/service/user/{user_id}/service/{service_id}`

Remove a service selection for a user.

**Response:**
```json
{
    "success": true,
    "message": "Service 'Delivery' removed from user 1",
    "user_id": 1,
    "service_id": 1
}
```

## Usage Examples

### Example 1: Text Input
```bash
curl -X POST "http://localhost:8000/service/select" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "service_text": "Delivery",
    "input_type": "text"
  }'
```

### Example 2: Voice Input
```bash
curl -X POST "http://localhost:8000/service/select" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "service_text": "I want delivery at my house",
    "input_type": "voice"
  }'
```

### Example 3: Get User Services
```bash
curl -X GET "http://localhost:8000/service/user/1"
```

### Example 4: Get Available Services
```bash
curl -X GET "http://localhost:8000/service/available"
```

## AI Service Detection

The voice input uses Google's Gemini AI to detect services from natural language text. The AI can:

- Detect single services: "I want delivery"
- Detect multiple services: "I need both delivery and catering"
- Handle complex statements: "I want delivery at my house and also need catering for an event"
- Understand various phrasings and synonyms

### Supported Service Phrases

#### Delivery
- "I want delivery at my house"
- "Please deliver my order to my home"
- "I need home delivery"
- "Can you send it to my address?"
- "Bring it to my place"

#### Pickup
- "I'll pick it up myself"
- "I want takeaway"
- "I'll come and collect it"
- "I'll grab it from the restaurant"
- "I prefer self-pickup"

#### Reservation
- "I want to make a reservation"
- "Book a table for me"
- "I need a table for dining"
- "Reserve a spot for us"

#### Catering
- "I need catering for my event"
- "Can you provide food service for a party?"
- "I want catering at my office"
- "Looking for bulk catering"
- "I need a catering service"

#### Events
- "I want to book for an event"
- "Need service for a celebration"
- "I'm planning an event, can you handle it?"
- "Looking for event support"
- "I want food for a special occasion"

## Error Handling

The API returns appropriate HTTP status codes:

- `200`: Success
- `400`: Bad Request (invalid input, validation errors)
- `404`: Not Found (service not found, user service not found)
- `500`: Internal Server Error (AI service errors, database errors)

## Configuration

### Environment Variables
Make sure to set the following environment variable:
```bash
GEMINI_API_KEY=your_gemini_api_key_here
```

### Database Migration
Run the migration to create the services tables:
```bash
alembic upgrade head
```

## Testing

Use the provided test script to test the API:
```bash
python test_service_api.py
```

The test script includes:
- Basic functionality tests
- Example scenario tests
- User service management tests
- Error handling tests

## Integration with Existing System

The service selection integrates with the existing system:

1. **User Management**: Links with existing user system
2. **AI Services**: Uses the same Gemini AI service as other features
3. **Database**: Follows the same patterns as other models
4. **Router**: Integrated with the main API router

## Example Scenarios

Based on the requirements, here are the example scenarios:

### Delivery Examples
- "I want delivery at my house" → Detects Delivery
- "Please deliver my order to my home" → Detects Delivery
- "I need home delivery" → Detects Delivery

### Pickup Examples
- "I'll pick it up myself" → Detects Pickup
- "I want takeaway" → Detects Pickup
- "I'll come and collect it" → Detects Pickup

### Catering Examples
- "I need catering for my event" → Detects Catering
- "Can you provide food service for a party?" → Detects Catering
- "I want catering at my office" → Detects Catering

### Events Examples
- "I want to book for an event" → Detects Events
- "I'm planning an event, can you handle it?" → Detects Events
- "Looking for event support" → Detects Events

## Future Enhancements

- Service preference persistence across sessions
- Service-specific content delivery
- Service recommendation based on user history
- Integration with order management system
- Service availability checking
- Service-specific pricing and options

