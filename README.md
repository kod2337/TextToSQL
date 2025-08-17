# 🧠 Text-to-SQL Assistant

A natural language AI assistant that converts user questions into **SQL queries** and executes them on a relational database.

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- Virtual environment (recommended)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd TextToSQL
```

2. Create and activate virtual environment:
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env file with your configuration
```

5. Run the application:
```bash
# Option 1: Direct FastAPI server
uvicorn src.api.app:app --host 0.0.0.0 --port 8001 --reload

# Option 2: Using main.py
python main.py
```

The API will be available at: http://localhost:8001

## 📖 API Documentation

Once the application is running, visit:
- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc
- **Web Interface**: http://localhost:8001/ (Interactive UI for testing)

### Key Endpoints

- `POST /api/text-to-sql` - Convert natural language to SQL
- `GET /api/health` - Application health check
- `GET /api/schema` - Get database schema information
- `POST /api/sql/validate` - Validate SQL queries
- `POST /api/sql/execute` - Execute SQL queries safely

## 🛠️ Development

### Project Structure
```
TextToSQL/
├── src/
│   ├── api/          # FastAPI application & routes
│   │   ├── app.py    # Main FastAPI application
│   │   ├── routes.py # API endpoints
│   │   ├── models.py # Pydantic models
│   │   └── web_routes.py # Web interface routes
│   ├── database/     # Database models and operations
│   ├── llm/          # LLM integration and text-to-SQL conversion
│   └── utils/        # Utility functions and helpers
├── web/              # Web interface
│   ├── templates/    # HTML templates
│   └── static/       # CSS, JS, and other static files
├── config/           # Configuration settings
├── data/             # Database files
├── logs/             # Application logs
├── tests/            # Test files
├── demo/             # Demo scripts
├── debug/            # Debug utilities
├── main.py           # Application entry point
└── requirements.txt  # Python dependencies
```

### Running Tests
```bash
pytest tests/ -v
```

### Code Formatting
```bash
black src/ tests/
flake8 src/ tests/
```

## 🚀 Usage Examples

### Using the Web Interface
1. Start the server: `uvicorn src.api.app:app --reload --port 8001`
2. Open your browser to: http://localhost:8001
3. Type natural language queries like:
   - "Show me all customers from New York"
   - "What are the top 5 products by sales?"
   - "Find users who registered last month"

### Using the API Directly
```python
import requests

response = requests.post("http://localhost:8001/api/text-to-sql", json={
    "question": "Show me all customers from New York"
})

print(response.json())
```

## 🎯 Project Status

### ✅ Completed Phases
- ✅ **Phase 1**: Project Setup & Foundation
- ✅ **Phase 2**: Database Layer & Configuration  
- ✅ **Phase 3**: Core SQL Generation Pipeline
- ✅ **Phase 4**: Query Execution & Safety
- ✅ **Phase 5**: REST API Development & Web Interface

### 🚧 Current Phase
- 🚧 **Phase 6**: Testing & Quality Assurance (Next)

### ⏳ Upcoming Phases
- ⏳ **Phase 7**: Advanced Features & Optimization
- ⏳ **Phase 8**: Production Deployment & Documentation

## 🌟 Key Features Implemented

### 🔧 **Core Functionality**
- Natural language to SQL conversion using OpenAI GPT models
- PostgreSQL database integration with Supabase
- Safe query execution with validation and sanitization
- Comprehensive error handling and logging

### 🌐 **REST API (FastAPI)**
- RESTful endpoints with automatic OpenAPI documentation
- Request/response validation using Pydantic models
- CORS support for cross-origin requests
- Health monitoring and status endpoints

### 💻 **Web Interface**
- Modern, responsive web UI with Tailwind CSS
- Interactive query builder with real-time feedback
- SQL syntax highlighting and formatting
- Schema exploration and table browsing

### 🛡️ **Security & Safety**
- SQL injection prevention through parameterized queries
- Query validation before execution
- Environment-based configuration management
- Comprehensive error handling without data exposure

## 📝 License

This project is licensed under the MIT License.
