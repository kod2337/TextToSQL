# 🌐 Text-to-SQL Assistant REST API Documentation

## Overview

The Text-to-SQL Assistant REST API provides programmatic access to natural language to SQL conversion capabilities. The API is built with FastAPI and includes comprehensive error handling, validation, and documentation.

## Base URL

```
http://localhost:8000
```

## API Version

```
http://localhost:8000/api/v1
```

## Interactive Documentation

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

---

## 🔧 **Server Management**

### Start the Server

```bash
# Method 1: Using the server script
python server.py

# Method 2: Using uvicorn directly
python -m uvicorn src.api.app:create_app --factory --host 127.0.0.1 --port 8000 --reload

# Method 3: Using the development utility
python dev.py
# Choose option 10: Start API Server
```

### Development Testing

```bash
# Run API tests
python tests/test_api.py

# Or use the development utility
python dev.py
# Choose option 11: Test API Endpoints
```

---

## 📋 **API Endpoints**

### 🏥 **Health Check Endpoints**

#### Basic Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy" | "degraded",
  "app_name": "Text-to-SQL Assistant",
  "version": "1.0.0",
  "database_status": "connected" | "disconnected"
}
```

#### Comprehensive Health Check
```http
GET /api/v1/health
```

**Response:**
```json
{
  "status": "healthy" | "degraded",
  "app_name": "Text-to-SQL Assistant", 
  "version": "1.0.0",
  "timestamp": "2025-08-17T22:35:50.613980",
  "database_status": "connected" | "disconnected",
  "ai_status": "ready" | "unavailable"
}
```

### 🧠 **Text-to-SQL Conversion**

#### Convert Text to SQL
```http
POST /api/v1/text-to-sql
```

**Request Body:**
```json
{
  "question": "Show me all customers from New York",
  "execute_query": false,
  "include_schema": true
}
```

**Request Parameters:**
- `question` (required): Natural language question to convert to SQL
- `execute_query` (optional, default: false): Whether to execute the generated SQL
- `include_schema` (optional, default: true): Include database schema in response

**Response:**
```json
{
  "success": true,
  "sql": {
    "sql_query": "SELECT * FROM customers WHERE city = 'New York';",
    "confidence_score": 85.5,
    "question_extracted": "Show me all customers from New York",
    "execution_time_ms": 125.5
  },
  "results": {
    "rows": [
      {"id": 1, "name": "John Doe", "city": "New York"},
      {"id": 2, "name": "Jane Smith", "city": "New York"}
    ],
    "row_count": 2,
    "columns": ["id", "name", "city"],
    "execution_time_ms": 45.2
  },
  "error": null,
  "schema_info": {...}
}
```

**Error Response:**
```json
{
  "success": false,
  "sql": {
    "sql_query": "",
    "confidence_score": 0.0,
    "question_extracted": "Show me all customers from New York",
    "execution_time_ms": 125.5
  },
  "results": null,
  "error": "Database connection failed",
  "schema_info": null
}
```

### 📊 **Database Schema**

#### Get Database Schema
```http
GET /api/v1/schema
```

**Response:**
```json
{
  "tables": {
    "customers": {
      "columns": ["id", "name", "email", "city"],
      "row_count": 150
    },
    "orders": {
      "columns": ["id", "customer_id", "total", "order_date"],
      "row_count": 342
    }
  },
  "table_count": 2
}
```

### 🔍 **SQL Validation**

#### Validate SQL Query
```http
GET /api/v1/validate-sql?query=SELECT * FROM customers;
```

**Parameters:**
- `query` (required): SQL query to validate

**Response:**
```json
{
  "valid": true,
  "error": null,
  "query": "SELECT * FROM customers;"
}
```

**Invalid Query Response:**
```json
{
  "valid": false,
  "error": "Only SELECT queries are allowed",
  "query": "DROP TABLE customers;"
}
```

---

## 📝 **Usage Examples**

### Python Requests Example

```python
import requests
import json

# Basic text-to-SQL conversion
response = requests.post('http://localhost:8000/api/v1/text-to-sql', json={
    "question": "How many customers do we have?",
    "execute_query": False
})

result = response.json()
if result['success']:
    print(f"Generated SQL: {result['sql']['sql_query']}")
    print(f"Confidence: {result['sql']['confidence_score']}%")
else:
    print(f"Error: {result['error']}")
```

### cURL Example

```bash
# Text-to-SQL conversion
curl -X POST "http://localhost:8000/api/v1/text-to-sql" \
     -H "Content-Type: application/json" \
     -d '{
       "question": "Show me the top 5 customers by total spending",
       "execute_query": true
     }'

# Get database schema
curl "http://localhost:8000/api/v1/schema"

# Health check
curl "http://localhost:8000/health"
```

### JavaScript Fetch Example

```javascript
// Text-to-SQL with execution
const response = await fetch('http://localhost:8000/api/v1/text-to-sql', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        question: 'Find all orders from the last month',
        execute_query: true,
        include_schema: false
    })
});

const result = await response.json();
console.log('SQL:', result.sql.sql_query);
console.log('Results:', result.results);
```

---

## ⚡ **Performance & Limits**

### Rate Limiting
- Default: No explicit rate limiting (configure in production)
- Groq API: 6,000 requests/hour (free tier)

### Query Execution Limits
- **Timeout**: 30 seconds per query
- **Complexity**: Limited to prevent resource exhaustion
- **Safety**: Only SELECT queries allowed
- **Row Limit**: Configurable (default: 1000 rows)

### Response Times
- **SQL Generation**: ~1-3 seconds
- **Query Execution**: ~50-500ms (depending on complexity)
- **Schema Retrieval**: ~100-200ms

---

## 🔒 **Security Features**

### SQL Safety
- ✅ Only SELECT queries allowed
- ✅ DROP, DELETE, INSERT operations blocked
- ✅ System schema access prevented
- ✅ Query complexity validation
- ✅ Timeout protection

### Input Validation
- ✅ Request schema validation with Pydantic
- ✅ SQL injection prevention
- ✅ Parameter sanitization
- ✅ Error message sanitization

### CORS Configuration
- Currently allows all origins (configure for production)
- Supports credentials and all HTTP methods
- Custom headers allowed

---

## 🚨 **Error Handling**

### HTTP Status Codes
- `200 OK`: Successful request
- `400 Bad Request`: Invalid request parameters
- `500 Internal Server Error`: Server error

### Error Response Format
```json
{
  "success": false,
  "error": "Descriptive error message",
  "error_code": "ERROR_TYPE",
  "details": {
    "additional": "context"
  }
}
```

### Common Error Types
- `SQL_VALIDATION_ERROR`: Generated SQL failed validation
- `DATABASE_CONNECTION_ERROR`: Database connectivity issues
- `AI_SERVICE_ERROR`: Groq API or model issues
- `TIMEOUT_ERROR`: Query execution timeout
- `INVALID_REQUEST`: Request validation failure

---

## 🔧 **Development & Testing**

### Running Tests
```bash
# Full API test suite
python tests/test_api.py

# Individual endpoint tests
python -c "import requests; print(requests.get('http://localhost:8000/health').json())"
```

### Development Server
```bash
# Start with auto-reload
python server.py

# Or with uvicorn directly
uvicorn src.api.app:create_app --factory --reload --host 127.0.0.1 --port 8000
```

### API Documentation
- Access Swagger UI at `http://localhost:8000/docs`
- Interactive testing available in the browser
- Complete API schema available

---

## 🚀 **Production Deployment**

### Configuration
1. **Environment Variables**: Configure database, API keys
2. **CORS**: Restrict allowed origins
3. **Rate Limiting**: Implement proper rate limiting
4. **Authentication**: Add API key or JWT authentication
5. **Monitoring**: Add logging and metrics collection

### Docker Deployment (Future)
```dockerfile
# Dockerfile example for production
FROM python:3.11-slim
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . /app
WORKDIR /app
EXPOSE 8000
CMD ["uvicorn", "src.api.app:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 📚 **Next Steps**

Phase 5 is now **COMPLETE** ✅! Your REST API includes:

- ✅ **FastAPI Framework**: Modern, fast, and well-documented
- ✅ **Comprehensive Endpoints**: Health, text-to-SQL, schema, validation
- ✅ **Request/Response Models**: Fully typed with Pydantic
- ✅ **Error Handling**: Robust error responses and logging
- ✅ **Interactive Documentation**: Swagger UI and ReDoc
- ✅ **Security Features**: SQL safety and input validation
- ✅ **Testing Suite**: Complete API endpoint testing

**Ready for Phase 6: Testing & Quality Assurance** 🧪
