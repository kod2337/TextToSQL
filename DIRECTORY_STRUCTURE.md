# Project Directory Structure

```
TextToSQL/
├── 📁 src/                     # Main source code
│   ├── 📁 llm/                 # AI/LLM integration
│   │   ├── generator.py        # Groq API integration
│   │   └── pipeline.py         # Main text-to-SQL pipeline
│   ├── 📁 query/               # Query processing
│   │   └── executor.py         # Safe SQL execution
│   ├── 📁 database/            # Database utilities
│   │   └── connection.py       # Database connection management
│   └── 📁 utils/               # Utility functions
│       └── settings.py         # Configuration management
│
├── 📁 tests/                   # Test files
│   ├── test_db.py              # Database tests
│   ├── test_groq.py            # Groq API tests
│   ├── test_groq_direct.py     # Direct API tests
│   ├── test_phase4.py          # Phase 4 functionality tests
│   ├── test_end_to_end.py      # End-to-end pipeline tests
│   └── README.md               # Test documentation
│
├── 📁 demo/                    # Demonstration scripts
│   ├── demo_complete_system.py # Complete system demo
│   └── README.md               # Demo documentation
│
├── 📁 debug/                   # Debug utilities
│   ├── debug_extraction.py     # Question extraction debugging
│   ├── debug_prompt.py         # Prompt debugging
│   ├── debug_sql.py            # SQL generation debugging
│   └── README.md               # Debug documentation
│
├── 📁 config/                  # Configuration files
│   └── database.py             # Database configuration
│
├── 📁 data/                    # Data files
│   └── sample_data.sql         # Sample database data
│
├── 📁 logs/                    # Log files
│   └── (generated log files)
│
├── 📁 .venv/                   # Python virtual environment
│
├── 📄 main.py                  # Main application entry point
├── 📄 requirements.txt         # Python dependencies
├── 📄 .env.example            # Environment variables template
├── 📄 .env                    # Environment variables (private)
├── 📄 README.md               # Project documentation
├── 📄 project.md              # Project overview
├── 📄 IMPLEMENTATION_PLAN.md  # Development phases
└── 📄 SUPABASE_SETUP.md       # Database setup guide
```

## Directory Purposes

### 🏗️ **Core Application (`src/`)**
- Main source code organized by functionality
- Clean separation of concerns (AI, database, utilities)
- Production-ready code modules

### 🧪 **Testing (`tests/`)**
- Unit tests for individual components
- Integration tests for system workflows
- End-to-end validation scripts

### 🎭 **Demonstrations (`demo/`)**
- Interactive system demonstrations
- Feature showcases for stakeholders
- Performance benchmarking scripts

### 🔧 **Development Tools (`debug/`)**
- Debugging utilities for development
- Issue isolation and troubleshooting
- Development workflow helpers

### ⚙️ **Configuration (`config/`)**
- Application configuration files
- Database and API settings
- Environment-specific configurations

### 💾 **Data (`data/`)**
- Sample data and database schemas
- Test datasets
- Migration scripts

## Benefits of This Structure

- **🎯 Clear Organization**: Easy to find specific functionality
- **🔍 Separation of Concerns**: Tests, demos, and debug tools isolated
- **👥 Team Collaboration**: Clear responsibilities and ownership
- **🚀 Scalability**: Easy to add new components in logical places
- **📚 Documentation**: Each directory has its own README
