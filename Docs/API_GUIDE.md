# 🔌 REST API Guide - GenAI Document Intelligence Platform

## 📋 Overview

The GenAI Document Intelligence Platform provides a comprehensive REST API built with FastAPI, offering programmatic access to all document processing and AI chat capabilities. This guide covers authentication, endpoints, request/response formats, and integration examples.

## 🚀 Getting Started

### Starting the API Server

The REST API runs alongside the Streamlit web interface:

```bash
# Start the main application (includes both Web UI and API)
streamlit run Modular_App/app.py

# Or start API server only
uvicorn Modular_App.api:app --reload --host 0.0.0.0 --port 8000
```

- **API Base URL**: `http://localhost:8000`
- **Interactive Documentation**: `http://localhost:8000/docs`
- **OpenAPI Schema**: `http://localhost:8000/openapi.json`

## 🔐 Authentication

The API uses JWT (JSON Web Token) based authentication with graceful fallback support.

### Default User Credentials

The system comes with default test credentials:

- **Username**: `admin` | **Password**: `password123`
- **Username**: `user` | **Password**: `userpass`

> ⚠️ **Security Note**: Change these default credentials in production environments.

### Obtaining an Access Token

**Endpoint**: `POST /auth/token`

```bash
curl -X POST "http://localhost:8000/auth/token" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "password123"
  }'
```

**Response:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

> **Note**: Tokens expire after 24 hours (86400 seconds). The system automatically handles JWT unavailability with simple token fallback.

### Using the Token

Include the token in the Authorization header for all subsequent requests:

```bash
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## 📡 API Endpoints

### 🏥 Health & Status

#### GET /health

Check API server health and status.

**Request:**

```bash
curl -X GET "http://localhost:8000/health"
```

**Response:**

```json
{
  "status": "healthy",
  "version": "3.0.0",
  "timestamp": "2025-09-28T10:30:00Z",
  "services": {
    "vector_store": "active",
    "ai_providers": ["openai", "anthropic", "google"],
    "supported_formats": ["pdf", "docx", "xlsx", "pptx", "txt"]
  }
}
```

### 📄 Document Management

#### POST /upload

Upload and process documents in multiple formats.

**Request:**

```bash
curl -X POST "http://localhost:8000/upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "files=@document.pdf" \
  -F "files=@spreadsheet.xlsx" \
  -F "files=@presentation.pptx" \
  -F "database_type=faiss"
```

**Response:**

```json
{
  "success": true,
  "message": "Documents processed successfully",
  "processed_files": [
    {
      "filename": "document.pdf",
      "format": "pdf",
      "pages": 10,
      "language": "english",
      "chunks_created": 25,
      "processing_time": 2.34
    },
    {
      "filename": "spreadsheet.xlsx",
      "format": "xlsx",
      "sheets": 3,
      "language": "english",
      "chunks_created": 15,
      "processing_time": 1.87
    }
  ],
  "total_chunks": 40,
  "vector_store_status": "updated"
}
```

#### GET /documents/list

List all processed documents.

**Request:**

```bash
curl -X GET "http://localhost:8000/documents/list" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**

```json
{
  "documents": [
    {
      "id": "doc_123",
      "filename": "report.pdf",
      "format": "pdf",
      "upload_date": "2025-09-28T10:00:00Z",
      "language": "english",
      "chunk_count": 25,
      "file_size": 2048576
    }
  ],
  "total_documents": 1,
  "total_chunks": 25
}
```

#### DELETE /documents/{document_id}

Remove a specific document from the system.

**Request:**

```bash
curl -X DELETE "http://localhost:8000/documents/doc_123" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**

```json
{
  "success": true,
  "message": "Document removed successfully",
  "document_id": "doc_123",
  "chunks_removed": 25
}
```

### 💬 Chat & Conversations

#### POST /chat/message

Send a message and get an AI response based on processed documents.

**Request:**

```bash
curl -X POST "http://localhost:8000/chat/message" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are the key findings in the uploaded documents?",
    "session_id": "user_session_123",
    "max_tokens": 500,
    "temperature": 0.7
  }'
```

**Response:**

```json
{
  "response": "Based on the uploaded documents, the key findings include...",
  "session_id": "user_session_123",
  "message_id": "msg_456",
  "timestamp": "2025-09-28T10:30:00Z",
  "source_documents": [
    {
      "document": "report.pdf",
      "page": 3,
      "relevance_score": 0.89
    }
  ],
  "token_usage": {
    "prompt_tokens": 1234,
    "completion_tokens": 567,
    "total_tokens": 1801
  },
  "processing_time": 2.15
}
```

#### GET /chat/history/{session_id}

Retrieve conversation history for a specific session.

**Request:**

```bash
curl -X GET "http://localhost:8000/chat/history/user_session_123" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**

```json
{
  "session_id": "user_session_123",
  "messages": [
    {
      "message_id": "msg_455",
      "type": "user",
      "content": "What are the key findings?",
      "timestamp": "2025-09-28T10:29:00Z"
    },
    {
      "message_id": "msg_456",
      "type": "assistant",
      "content": "Based on the uploaded documents...",
      "timestamp": "2025-09-28T10:30:00Z",
      "source_documents": [...]
    }
  ],
  "total_messages": 2
}
```

#### DELETE /chat/history/{session_id}

Clear conversation history for a session.

**Request:**

```bash
curl -X DELETE "http://localhost:8000/chat/history/user_session_123" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### ⚙️ Configuration & Settings

#### GET /config/providers

List available AI providers and their models.

**Request:**

```bash
curl -X GET "http://localhost:8000/config/providers" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**

```json
{
  "providers": {
    "openai": {
      "available": true,
      "models": ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo-preview"],
      "default_model": "gpt-3.5-turbo"
    },
    "anthropic": {
      "available": true,
      "models": ["claude-3-haiku-20240307", "claude-3-sonnet-20240229", "claude-3-opus-20240229"],
      "default_model": "claude-3-sonnet-20240229"
    },
    "google": {
      "available": true,
      "models": ["gemini-pro", "gemini-pro-vision"],
      "default_model": "gemini-pro"
    },
    "local": {
      "available": false,
      "models": [],
      "note": "Requires Ollama installation"
    }
  },
  "current_provider": "openai",
  "current_model": "gpt-3.5-turbo"
}
```

#### POST /config/provider

Switch AI provider and model.

**Request:**

```bash
curl -X POST "http://localhost:8000/config/provider" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "anthropic",
    "model": "claude-3-sonnet-20240229"
  }'
```

**Response:**

```json
{
  "success": true,
  "message": "Provider switched successfully",
  "provider": "anthropic",
  "model": "claude-3-sonnet-20240229",
  "provider_status": "active"
}
```

#### GET /config/languages

List supported languages and current language settings.

**Request:**

```bash
curl -X GET "http://localhost:8000/config/languages" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**

```json
{
  "supported_languages": [
    "english", "spanish", "french", "german", "italian",
    "portuguese", "russian", "chinese", "japanese", 
    "korean", "arabic", "hindi"
  ],
  "auto_detection": true,
  "default_language": "english"
}
```

### 🗄️ Vector Store Management

#### GET /vector-store/status

Get vector store status and statistics.

**Request:**

```bash
curl -X GET "http://localhost:8000/vector-store/status" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**

```json
{
  "type": "faiss",
  "status": "active",
  "total_documents": 5,
  "total_chunks": 150,
  "index_size": "2.3MB",
  "last_updated": "2025-09-28T10:30:00Z"
}
```

#### POST /vector-store/rebuild

Rebuild the vector store index.

**Request:**

```bash
curl -X POST "http://localhost:8000/vector-store/rebuild" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**

```json
{
  "success": true,
  "message": "Vector store rebuilt successfully",
  "processing_time": 15.67,
  "total_chunks_indexed": 150
}
```

## 📊 Response Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 413 | Payload Too Large |
| 422 | Validation Error |
| 500 | Internal Server Error |

## 🚨 Error Handling

All API errors follow a consistent format:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid file format",
    "details": {
      "field": "files",
      "supported_formats": ["pdf", "docx", "xlsx", "pptx", "txt"]
    },
    "timestamp": "2025-09-28T10:30:00Z"
  }
}
```

Common error codes:

- `AUTHENTICATION_FAILED`
- `VALIDATION_ERROR`
- `DOCUMENT_PROCESSING_ERROR`
- `PROVIDER_UNAVAILABLE`
- `RATE_LIMIT_EXCEEDED`
- `FILE_TOO_LARGE`

## 🔧 Integration Examples

### Python Client Example

```python
import requests
import json

class GenAIClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.token = None
    
    def authenticate(self, username="admin", password="password123"):
        response = requests.post(
            f"{self.base_url}/auth/token",
            json={"username": username, "password": password}
        )
        if response.status_code == 200:
            self.token = response.json()["access_token"]
            return True
        return False
    
    def upload_document(self, file_path):
        headers = {"Authorization": f"Bearer {self.token}"}
        files = {"files": open(file_path, "rb")}
        response = requests.post(
            f"{self.base_url}/documents/upload",
            headers=headers,
            files=files
        )
        return response.json()
    
    def chat(self, message, session_id="default"):
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        data = {
            "message": message,
            "session_id": session_id
        }
        response = requests.post(
            f"{self.base_url}/chat/message",
            headers=headers,
            json=data
        )
        return response.json()

# Usage
client = GenAIClient()
client.authenticate()
client.upload_document("document.pdf")
response = client.chat("What is the main topic of the document?")
print(response["response"])
```

### JavaScript/Node.js Example

```javascript
const axios = require('axios');

class GenAIClient {
  constructor(baseURL = 'http://localhost:8000') {
    this.baseURL = baseURL;
    this.token = null;
  }

  async authenticate(username = 'admin', password = 'password123') {
    try {
      const response = await axios.post(`${this.baseURL}/auth/token`, {
        username,
        password
      });
      this.token = response.data.access_token;
      return true;
    } catch (error) {
      console.error('Authentication failed:', error.response.data);
      return false;
    }
  }

  async uploadDocument(filePath) {
    const FormData = require('form-data');
    const fs = require('fs');
    
    const form = new FormData();
    form.append('files', fs.createReadStream(filePath));

    try {
      const response = await axios.post(
        `${this.baseURL}/documents/upload`,
        form,
        {
          headers: {
            ...form.getHeaders(),
            'Authorization': `Bearer ${this.token}`
          }
        }
      );
      return response.data;
    } catch (error) {
      console.error('Upload failed:', error.response.data);
      throw error;
    }
  }

  async chat(message, sessionId = 'default') {
    try {
      const response = await axios.post(
        `${this.baseURL}/chat/message`,
        {
          message,
          session_id: sessionId
        },
        {
          headers: {
            'Authorization': `Bearer ${this.token}`,
            'Content-Type': 'application/json'
          }
        }
      );
      return response.data;
    } catch (error) {
      console.error('Chat failed:', error.response.data);
      throw error;
    }
  }
}

// Usage
(async () => {
  const client = new GenAIClient();
  await client.authenticate();
  await client.uploadDocument('document.pdf');
  const response = await client.chat('What is the main topic?');
  console.log(response.response);
})();
```

## 📈 Rate Limiting

The API implements rate limiting to ensure fair usage:

- **Authentication**: 10 requests per minute
- **Document Upload**: 5 requests per minute
- **Chat Messages**: 30 requests per minute
- **Other Endpoints**: 60 requests per minute

Rate limit information is included in response headers:

- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Remaining requests
- `X-RateLimit-Reset`: Reset timestamp

## 🔒 Security Considerations

1. **HTTPS**: Always use HTTPS in production
2. **API Keys**: Store API tokens securely
3. **File Validation**: Only upload trusted documents
4. **Input Sanitization**: Validate all user inputs
5. **Access Control**: Implement proper user authentication
6. **Rate Limiting**: Monitor and respect rate limits

## 📞 Support & Resources

- **Interactive Documentation**: `http://localhost:8000/docs`
- **OpenAPI Schema**: `http://localhost:8000/openapi.json`
- **GitHub Repository**: [Project Repository URL]
- **Issue Tracking**: [Issues URL]
