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
python main.py
```

The API will be available at: http://localhost:8000

## 📖 API Documentation

Once the application is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🛠️ Development

### Project Structure
```
TextToSQL/
├── src/
│   ├── api/          # FastAPI application
│   ├── database/     # Database models and operations
│   ├── llm/          # LLM integration and text-to-SQL conversion
│   └── utils/        # Utility functions and helpers
├── config/           # Configuration settings
├── data/             # Database files
├── logs/             # Application logs
├── tests/            # Test files
├── main.py           # Application entry point
└── requirements.txt  # Python dependencies
```

### Running Tests
```bash
pytest tests/
```

### Code Formatting
```bash
black src/ tests/
flake8 src/ tests/
```

## 🎯 Features

- ✅ **Phase 1**: Project Setup & Foundation
- 🚧 **Phase 2**: Database Layer (In Progress)
- ⏳ **Phase 3**: Core SQL Generation
- ⏳ **Phase 4**: Query Execution & Safety
- ⏳ **Phase 5**: API Development
- ⏳ **Phase 6**: Testing & Quality Assurance
- ⏳ **Phase 7**: Advanced Features
- ⏳ **Phase 8**: User Interface & Documentation

## 📝 License

This project is licensed under the MIT License.
