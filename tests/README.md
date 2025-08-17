# Tests Directory

This directory contains all test files for the Text-to-SQL Assistant project.

## Test Files

### Unit Tests
- `test_db.py` - Database connection and basic query tests
- `test_groq.py` - Groq API integration tests
- `test_groq_direct.py` - Direct Groq API connection tests

### Integration Tests
- `test_phase4.py` - Phase 4 functionality tests (Query Execution & Safety)
- `test_end_to_end.py` - Complete pipeline end-to-end tests

## Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_db.py

# Run with verbose output
python -m pytest tests/ -v

# Run individual test files directly
python tests/test_groq.py
python tests/test_phase4.py
```

## Test Categories

- **Database Tests**: Verify database connectivity and schema access
- **AI Integration Tests**: Test Groq API functionality and SQL generation
- **Security Tests**: Validate query safety and validation systems
- **Pipeline Tests**: End-to-end system functionality verification
