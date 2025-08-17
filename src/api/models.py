"""
Pydantic models for API requests and responses
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from decimal import Decimal


class TextToSQLRequest(BaseModel):
    """Request model for text-to-SQL conversion"""
    question: str = Field(..., description="Natural language question to convert to SQL")
    execute_query: bool = Field(default=False, description="Whether to execute the generated SQL query")
    include_schema: bool = Field(default=True, description="Whether to include schema information in the response")
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "Show me all customers from New York",
                "execute_query": True,
                "include_schema": False
            }
        }


class SQLResponse(BaseModel):
    """Response model for SQL generation"""
    sql_query: str = Field(..., description="Generated SQL query")
    confidence_score: Optional[float] = Field(None, description="AI confidence score (0-100)")
    question_extracted: Optional[str] = Field(None, description="Extracted question from input")
    execution_time_ms: Optional[float] = Field(None, description="Query execution time in milliseconds")
    
    class Config:
        json_schema_extra = {
            "example": {
                "sql_query": "SELECT * FROM customers WHERE city = 'New York';",
                "confidence_score": 85.5,
                "question_extracted": "Show me all customers from New York",
                "execution_time_ms": 125.5
            }
        }


class QueryResult(BaseModel):
    """Model for query execution results"""
    rows: List[Dict[str, Any]] = Field(..., description="Query result rows")
    row_count: int = Field(..., description="Number of rows returned")
    columns: List[str] = Field(..., description="Column names")
    execution_time_ms: float = Field(..., description="Query execution time in milliseconds")
    
    class Config:
        json_schema_extra = {
            "example": {
                "rows": [
                    {"id": 1, "name": "John Doe", "city": "New York"},
                    {"id": 2, "name": "Jane Smith", "city": "New York"}
                ],
                "row_count": 2,
                "columns": ["id", "name", "city"],
                "execution_time_ms": 45.2
            }
        }


class TextToSQLResponse(BaseModel):
    """Complete response model for text-to-SQL requests"""
    success: bool = Field(..., description="Whether the request was successful")
    sql: SQLResponse = Field(..., description="SQL generation information")
    results: Optional[QueryResult] = Field(None, description="Query execution results (if executed)")
    error: Optional[str] = Field(None, description="Error message if request failed")
    schema_info: Optional[Dict[str, Any]] = Field(None, description="Database schema information")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "sql": {
                    "sql_query": "SELECT * FROM customers WHERE city = 'New York';",
                    "confidence_score": 85.5,
                    "question_extracted": "Show me all customers from New York",
                    "execution_time_ms": 125.5
                },
                "results": {
                    "rows": [{"id": 1, "name": "John Doe", "city": "New York"}],
                    "row_count": 1,
                    "columns": ["id", "name", "city"],
                    "execution_time_ms": 45.2
                },
                "error": None,
                "schema_info": None
            }
        }


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str = Field(..., description="Health status")
    app_name: str = Field(..., description="Application name")
    version: str = Field(..., description="Application version")
    timestamp: datetime = Field(default_factory=datetime.now, description="Health check timestamp")
    database_status: str = Field(..., description="Database connection status")
    ai_status: str = Field(..., description="AI service status")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "app_name": "Text-to-SQL Assistant",
                "version": "1.0.0",
                "timestamp": "2025-08-17T10:30:00",
                "database_status": "connected",
                "ai_status": "ready"
            }
        }


class SchemaResponse(BaseModel):
    """Database schema response model"""
    tables: Dict[str, Dict[str, Any]] = Field(..., description="Database tables and their information")
    table_count: int = Field(..., description="Number of tables in the database")
    
    class Config:
        json_schema_extra = {
            "example": {
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
        }


class ErrorResponse(BaseModel):
    """Error response model"""
    success: bool = Field(default=False, description="Always false for error responses")
    error: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code for programmatic handling")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error": "Invalid SQL query generated",
                "error_code": "SQL_VALIDATION_ERROR",
                "details": {
                    "query": "SELECT * FROM non_existent_table;",
                    "validation_error": "Table 'non_existent_table' does not exist"
                }
            }
        }
