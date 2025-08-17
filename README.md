# 🧠 Text-to-SQL Assistant

A natural language AI assistant powered by **LangChain** and **Groq** that converts user questions into **SQL queries** and executes them on a relational database with intelligent, conversational responses.

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

- `POST /api/v1/text-to-sql` - Convert natural language to SQL (Legacy)
- `POST /api/v1/langchain/text-to-sql` - LangChain-powered SQL generation with natural responses
- `POST /api/v1/langchain/analyze` - Advanced query analysis
- `GET /api/v1/langchain/memory/history` - Get conversation history
- `DELETE /api/v1/langchain/memory/clear` - Clear conversation memory
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

# Using the enhanced LangChain endpoint
response = requests.post("http://localhost:8001/api/v1/langchain/text-to-sql", json={
    "question": "Show me all customers from New York",
    "execute_query": True,
    "include_schema": True
})

result = response.json()
print("SQL:", result['sql']['sql_query'])
print("Answer:", result['sql']['natural_language_response'])
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
- **LangChain Framework Integration** - Advanced text-to-SQL conversion with memory and context
- **Groq LLM Integration** - Fast, efficient language model processing (llama-3.3-70b-versatile)
- **Natural Language Responses** - Conversational AI responses based on actual query results
- **PostgreSQL Database Integration** with Supabase cloud hosting
- **Safe Query Execution** with validation and sanitization
- **Conversation Memory** - Context-aware multi-turn conversations
- **Comprehensive Error Handling** and logging

### 🌐 **REST API (FastAPI)**
- **Dual API Support** - Both legacy and LangChain-powered endpoints
- **RESTful Endpoints** with automatic OpenAPI documentation
- **Request/Response Validation** using Pydantic models
- **CORS Support** for cross-origin requests
- **Health Monitoring** and status endpoints
- **Conversation Memory Management** APIs

### 💻 **Web Interface**
- **Streamlined Single-Button Interface** - "Ask AI Assistant" powered by LangChain
- **Modern, Responsive Design** with Tailwind CSS and Font Awesome icons
- **Real-time SQL Generation** with natural language explanations
- **SQL Syntax Highlighting** and formatting
- **Schema Exploration** and table browsing
- **Conversation History** tracking and display

### 🛡️ **Security & Safety**
- **SQL Injection Prevention** through parameterized queries and LangChain validation
- **Query Safety Checks** before execution
- **Environment-based Configuration** management
- **Comprehensive Error Handling** without data exposure
- **Natural Error Messages** - User-friendly responses instead of technical errors

### 🧠 **AI & Language Processing**
- **LangChain Framework** - Professional-grade LLM application framework
- **Groq Integration** - High-performance language model inference
- **Context-Aware Prompting** - Schema-informed SQL generation
- **Conversational Memory** - Multi-turn conversation support
- **Natural Language Explanations** - Business-friendly result interpretation

## 📝 License

This project is licensed under the MIT License.
