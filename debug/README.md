# Debug Directory

This directory contains debugging and development utility scripts for the Text-to-SQL Assistant project.

## Debug Scripts

### Core Debugging
- `debug_extraction.py` - Debug question extraction from prompts
- `debug_prompt.py` - Debug prompt generation and formatting
- `debug_sql.py` - Debug SQL generation and validation

## Usage

These scripts are designed for development and troubleshooting:

```bash
# Debug question extraction issues
python debug/debug_extraction.py

# Debug prompt formatting
python debug/debug_prompt.py

# Debug SQL generation
python debug/debug_sql.py
```

## When to Use

- **Question Extraction Issues**: Use `debug_extraction.py` when the AI isn't properly extracting questions from prompts
- **Prompt Problems**: Use `debug_prompt.py` when SQL generation quality is poor
- **SQL Validation**: Use `debug_sql.py` when queries are failing validation or execution

## Development Notes

These debug scripts help isolate issues in the pipeline:
1. Question extraction from natural language
2. Prompt construction for AI model
3. SQL generation and safety validation
