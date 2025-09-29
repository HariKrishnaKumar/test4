# Language Selection API

This document describes the Language Selection API endpoints that allow users to select or speak their preferred language.

## Overview

The Language Selection API provides two main input methods:
1. **Text Input**: Direct language selection via text
2. **Voice Input**: AI-powered language detection from voice text

## Features

- ✅ Text-based language selection
- ✅ Voice-based language detection using AI (Gemini)
- ✅ Multiple language detection from single input
- ✅ Session-based language storage
- ✅ Language validation
- ✅ Available languages management
- ✅ Language detection testing endpoint

## Database Schema

### Languages Table
```sql
CREATE TABLE languages (
    id INT PRIMARY KEY AUTO_INCREMENT,
    language_name VARCHAR(100) NOT NULL UNIQUE,
    language_code VARCHAR(10),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME ON UPDATE CURRENT_TIMESTAMP
);
```

### Session Table (Updated)
The existing `sessions` table stores the selected language:
```sql
CREATE TABLE sessions (
    id VARCHAR(100) PRIMARY KEY,
    user_id INT,
    language VARCHAR(10) NOT NULL,  -- Stores the selected language
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## API Endpoints

### 1. Select Language
**POST** `/language/select`

Select or detect language from text or voice input.

**Request Body:**
```json
{
    "session_id": "string",
    "user_id": "integer (optional)",
    "language_text": "string",
    "input_type": "text|voice"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Language 'Spanish' selected successfully",
    "selected_language": "Spanish",
    "session_id": "test_session_123",
    "user_id": 1,
    "detected_languages": ["Spanish"]  // Only for voice input
}
```

### 2. Get Session Language
**GET** `/language/session/{session_id}`

Get the current language for a session.

**Response:**
```json
{
    "success": true,
    "session_id": "test_session_123",
    "language": "Spanish"
}
```

### 3. Get Available Languages
**GET** `/language/available`

Get list of all available languages.

**Response:**
```json
[
    {
        "id": 1,
        "language_name": "English",
        "language_code": "en",
        "created_at": "2025-09-11T18:20:59.628501",
        "updated_at": null
    },
    // ... more languages
]
```

### 4. Add Language
**POST** `/language/available`

Add a new language to the available languages list.

**Request Body:**
```json
{
    "language_name": "string",
    "language_code": "string (optional)"
}
```

### 5. Detect Languages (Testing)
**POST** `/language/detect`

Detect languages from text using AI (for testing/debugging).

**Query Parameters:**
- `text`: The text to analyze

**Response:**
```json
{
    "success": true,
    "input_text": "I can speak French and German",
    "detected_languages": ["French", "German"],
    "primary_language": "French"
}
```

## Usage Examples

### Example 1: Text Input
```bash
curl -X POST "http://localhost:8000/language/select" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "user_123",
    "user_id": 1,
    "language_text": "Spanish",
    "input_type": "text"
  }'
```

### Example 2: Voice Input
```bash
curl -X POST "http://localhost:8000/language/select" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "user_123",
    "user_id": 1,
    "language_text": "I can speak French, but I also understand German",
    "input_type": "voice"
  }'
```

### Example 3: Get Session Language
```bash
curl -X GET "http://localhost:8000/language/session/user_123"
```

## AI Language Detection

The voice input uses Google's Gemini AI to detect languages from natural language text. The AI can:

- Detect single languages: "My language is Spanish"
- Detect multiple languages: "I can speak French and German"
- Handle negative statements: "I don't know Chinese" → defaults to English
- Handle complex statements: "I know all languages" → defaults to English

### Supported Languages

The system supports 30+ common languages including:
- English, Spanish, French, German, Italian, Portuguese
- Chinese, Japanese, Korean, Arabic, Hindi, Russian
- Dutch, Swedish, Norwegian, Danish, Finnish, Polish
- And many more...

## Error Handling

The API returns appropriate HTTP status codes:

- `200`: Success
- `400`: Bad Request (invalid input, validation errors)
- `404`: Not Found (session not found)
- `500`: Internal Server Error (AI service errors, database errors)

## Configuration

### Environment Variables
Make sure to set the following environment variable:
```bash
GEMINI_API_KEY=your_gemini_api_key_here
```

### Database Migration
Run the migration to create the languages table:
```bash
alembic upgrade head
```

## Testing

Use the provided test script to test the API:
```bash
python test_language_api.py
```

The test script includes:
- Basic functionality tests
- Example scenario tests
- Error handling tests

## Integration with Existing System

The language selection integrates with the existing conversation system:

1. **Session Management**: Uses the existing `sessions` table
2. **User Management**: Links with existing user system
3. **AI Services**: Uses the same Gemini AI service as voice processing
4. **Database**: Follows the same patterns as other models

## Example Scenarios

Based on the requirements, here are the example scenarios:

1. **"I don't know Chinese"** → Detects English as primary language
2. **"My language is Spanish"** → Detects Spanish as primary language
3. **"I can speak French, but I also understand German"** → Detects French and German, uses French as primary
4. **"I know all languages"** → Defaults to English

## Future Enhancements

- Language preference persistence across sessions
- Multi-language support in responses
- Language-specific content delivery
- Voice-to-text integration
- Language learning recommendations
