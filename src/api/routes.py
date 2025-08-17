"""
Main API routes for Text-to-SQL Assistant
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import time
import logging

from ..api.models import (
    TextToSQLRequest, 
    TextToSQLResponse, 
    SQLResponse, 
    QueryResult, 
    SchemaResponse,
    HealthResponse,
    ErrorResponse
)
from ..llm.pipeline import execute_text_to_sql, get_text_to_sql_pipeline
from ..database.connection import test_connection, get_schema_info
from ..query.executor import get_query_executor
from ..utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


async def get_pipeline():
    """Dependency to get the text-to-SQL pipeline"""
    try:
        return get_text_to_sql_pipeline()
    except Exception as e:
        logger.error(f"Failed to initialize pipeline: {e}")
        raise HTTPException(status_code=500, detail="Failed to initialize text-to-SQL pipeline")


async def check_database_health() -> str:
    """Check database connection health"""
    try:
        conn_info = test_connection()
        return "connected" if conn_info.get("success") else "disconnected"
    except Exception:
        return "disconnected"


async def check_ai_health() -> str:
    """Check AI service health"""
    try:
        pipeline = get_text_to_sql_pipeline()
        # Simple test query to verify AI is working
        result = pipeline.generate_sql("test query", "test schema")
        return "ready" if result else "unavailable"
    except Exception:
        return "unavailable"


@router.post("/text-to-sql", response_model=TextToSQLResponse)
async def convert_text_to_sql(
    request: TextToSQLRequest,
    pipeline = Depends(get_pipeline)
):
    """
    Convert natural language text to SQL query
    
    - **question**: Natural language question to convert to SQL
    - **execute_query**: Whether to execute the generated SQL query (default: False)
    - **include_schema**: Whether to include database schema in response (default: True)
    """
    start_time = time.time()
    
    try:
        logger.info(f"Processing text-to-SQL request: {request.question}")
        
        # Execute the text-to-SQL pipeline
        if request.execute_query:
            # Use the execute_text_to_sql function for full execution
            result = execute_text_to_sql(question=request.question)
            
            # Calculate execution time
            execution_time_ms = (time.time() - start_time) * 1000
            
            # Build SQL response
            sql_response = SQLResponse(
                sql_query=result.get("sql_query", ""),
                confidence_score=result.get("confidence", 0.0),
                question_extracted=result.get("question", request.question),
                execution_time_ms=execution_time_ms
            )
            
            # Build query results if executed successfully
            query_results = None
            if result.get("success") and result.get("data"):
                query_results = QueryResult(
                    rows=result.get("data", []),
                    row_count=result.get("row_count", 0),
                    columns=list(result["data"][0].keys()) if result.get("data") else [],
                    execution_time_ms=result.get("execution_time", 0.0)
                )
        else:
            # Use the pipeline for SQL generation only
            pipeline_result = pipeline.generate_sql(
                request.question,
                template_type="few_shot",
                include_metadata=True,
                execute_query=False
            )
            
            # Calculate execution time
            execution_time_ms = (time.time() - start_time) * 1000
            
            # Build SQL response for generation only
            sql_response = SQLResponse(
                sql_query=pipeline_result.query,
                confidence_score=pipeline_result.confidence,
                question_extracted=request.question,
                execution_time_ms=execution_time_ms
            )
            
            # Create a mock result structure for consistency
            result = {
                "success": True,
                "sql_query": pipeline_result.query,
                "confidence": pipeline_result.confidence,
                "question": request.question
            }
            query_results = None
        
        # Get schema info if requested
        schema_info = None
        if request.include_schema:
            try:
                schema_info = get_schema_info()
            except Exception as e:
                logger.warning(f"Failed to get schema info: {e}")
        
        response = TextToSQLResponse(
            success=True,
            sql=sql_response,
            results=query_results,
            error=None,
            schema_info=schema_info
        )
        
        # Calculate final execution time for logging
        final_execution_time_ms = (time.time() - start_time) * 1000
        logger.info(f"Successfully processed request in {final_execution_time_ms:.2f}ms")
        return response
        
    except Exception as e:
        logger.error(f"Error processing text-to-SQL request: {e}")
        
        # Return error response
        return TextToSQLResponse(
            success=False,
            sql=SQLResponse(
                sql_query="",
                confidence_score=0.0,
                question_extracted=request.question,
                execution_time_ms=(time.time() - start_time) * 1000
            ),
            results=None,
            error=str(e),
            schema_info=None
        )


@router.get("/schema", response_model=SchemaResponse)
async def get_database_schema():
    """
    Get database schema information
    
    Returns information about all tables, columns, and relationships in the database.
    """
    try:
        logger.info("Fetching database schema")
        
        schema_info = get_schema_info()
        
        # Transform schema info to match response model
        tables = {}
        for table_name, table_info in schema_info.get("tables", {}).items():
            tables[table_name] = {
                "columns": table_info.get("columns", []),
                "row_count": table_info.get("row_count", 0)
            }
        
        response = SchemaResponse(
            tables=tables,
            table_count=len(tables)
        )
        
        logger.info(f"Successfully retrieved schema for {len(tables)} tables")
        return response
        
    except Exception as e:
        logger.error(f"Error fetching database schema: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch database schema: {e}")


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Comprehensive health check endpoint
    
    Returns the health status of all system components including database and AI services.
    """
    try:
        logger.info("Performing health check")
        
        # Check database health
        db_status = await check_database_health()
        
        # Check AI health
        ai_status = await check_ai_health()
        
        # Determine overall status
        overall_status = "healthy" if db_status == "connected" and ai_status == "ready" else "degraded"
        
        from config.settings import get_settings
        settings = get_settings()
        
        response = HealthResponse(
            status=overall_status,
            app_name=settings.app_name,
            version=settings.app_version,
            database_status=db_status,
            ai_status=ai_status
        )
        
        logger.info(f"Health check completed: {overall_status}")
        return response
        
    except Exception as e:
        logger.error(f"Error during health check: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {e}")


@router.get("/validate-sql")
async def validate_sql_query(query: str):
    """
    Validate a SQL query without executing it
    
    - **query**: SQL query to validate
    """
    try:
        logger.info(f"Validating SQL query: {query[:100]}...")
        
        # Get query executor for validation
        executor = get_query_executor()
        
        # Validate the query
        validation_result = executor.validate_query(query)
        
        response = {
            "valid": validation_result.get("valid", False),
            "error": validation_result.get("error"),
            "query": query
        }
        
        logger.info(f"SQL validation result: {response['valid']}")
        return response
        
    except Exception as e:
        logger.error(f"Error validating SQL query: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to validate query: {e}")


@router.post("/langchain/text-to-sql", response_model=TextToSQLResponse)
async def convert_text_to_sql_langchain(
    request: TextToSQLRequest,
    pipeline=Depends(get_pipeline)
) -> TextToSQLResponse:
    """
    Convert natural language question to SQL using LangChain framework
    
    Enhanced features:
    - Conversation memory (remembers previous questions)
    - Agent analysis for complex queries
    - Improved prompt engineering with LangChain templates
    """
    start_time = time.time()
    
    try:
        logger.info(f"Converting text to SQL with LangChain: {request.question}")
        
        # Use LangChain for SQL generation with context
        if request.execute_query:
            pipeline_result = pipeline.generate_sql_with_context(
                request.question,
                execute_query=True
            )
        else:
            pipeline_result = pipeline.generate_sql_with_context(
                request.question,
                execute_query=False
            )
        
        # Calculate execution time
        execution_time_ms = (time.time() - start_time) * 1000
        
        # Build SQL response with natural language
        sql_response = SQLResponse(
            sql_query=pipeline_result.query,
            confidence_score=pipeline_result.confidence,
            question_extracted=request.question,
            execution_time_ms=execution_time_ms,
            natural_language_response=pipeline_result.metadata.get("natural_language_response") if pipeline_result.metadata else None,
            explanation=pipeline_result.metadata.get("langchain_explanation") if pipeline_result.metadata else None
        )
        
        # Build query results if executed
        query_results = None
        if pipeline_result.execution_result and pipeline_result.execution_result.success:
            query_results = QueryResult(
                rows=pipeline_result.execution_result.data,
                row_count=pipeline_result.execution_result.row_count,
                columns=list(pipeline_result.execution_result.data[0].keys()) if pipeline_result.execution_result.data else [],
                execution_time_ms=pipeline_result.execution_result.execution_time
            )
        
        # Get schema info if requested
        schema_info = None
        if request.include_schema:
            try:
                schema_data = get_schema_info()
                schema_info = {
                    "tables": list(schema_data.keys()),
                    "total_tables": len(schema_data),
                    "schema_details": schema_data
                }
            except Exception as e:
                logger.warning(f"Could not retrieve schema info: {e}")
        
        # Build response with LangChain metadata
        response = TextToSQLResponse(
            success=True,  # Add required success field
            sql=sql_response,
            results=query_results,
            schema_info=schema_info,  # Fixed field name
            error=None,  # Add required error field
            metadata={
                "method": "langchain",
                "conversation_memory": True,
                "langchain_metadata": pipeline_result.metadata or {}
            }
        )
        
        logger.info(f"LangChain text-to-SQL conversion completed successfully")
        return response
        
    except Exception as e:
        logger.error(f"Error processing LangChain text-to-SQL request: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process request: {str(e)}")


@router.post("/langchain/analyze", response_model=TextToSQLResponse)
async def analyze_complex_query(
    request: TextToSQLRequest,
    pipeline=Depends(get_pipeline)
) -> TextToSQLResponse:
    """
    Analyze complex queries using LangChain agent
    
    Features:
    - Step-by-step query breakdown
    - Table relationship analysis
    - Complex join reasoning
    - Multi-step query planning
    """
    start_time = time.time()
    
    try:
        logger.info(f"Analyzing complex query with LangChain agent: {request.question}")
        
        # Use LangChain agent for complex analysis
        pipeline_result = pipeline.analyze_complex_question(
            request.question,
            execute_query=request.execute_query
        )
        
        # Calculate execution time
        execution_time_ms = (time.time() - start_time) * 1000
        
        # Build SQL response with natural language
        sql_response = SQLResponse(
            sql_query=pipeline_result.query,
            confidence_score=pipeline_result.confidence,
            question_extracted=request.question,
            execution_time_ms=execution_time_ms,
            natural_language_response=pipeline_result.metadata.get("natural_language_response") if pipeline_result.metadata else None,
            explanation=pipeline_result.metadata.get("langchain_explanation") if pipeline_result.metadata else None
        )
        
        # Build query results if executed
        query_results = None
        if pipeline_result.execution_result and pipeline_result.execution_result.success:
            query_results = QueryResult(
                rows=pipeline_result.execution_result.data,
                row_count=pipeline_result.execution_result.row_count,
                columns=list(pipeline_result.execution_result.data[0].keys()) if pipeline_result.execution_result.data else [],
                execution_time_ms=pipeline_result.execution_result.execution_time
            )
        
        # Get schema info if requested
        schema_info = None
        if request.include_schema:
            try:
                schema_data = get_schema_info()
                schema_info = {
                    "tables": list(schema_data.keys()),
                    "total_tables": len(schema_data),
                    "schema_details": schema_data
                }
            except Exception as e:
                logger.warning(f"Could not retrieve schema info: {e}")
        
        # Build response with agent analysis
        response = TextToSQLResponse(
            success=True,  # Add required success field
            sql=sql_response,
            results=query_results,
            schema_info=schema_info,  # Fixed field name
            error=None,  # Add required error field
            metadata={
                "method": "langchain_agent",
                "agent_analysis": pipeline_result.metadata.get("agent_analysis") if pipeline_result.metadata else None,
                "langchain_metadata": pipeline_result.metadata or {}
            }
        )
        
        logger.info(f"LangChain agent analysis completed successfully")
        return response
        
    except Exception as e:
        logger.error(f"Error processing LangChain agent analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze query: {str(e)}")


@router.post("/langchain/memory/clear")
async def clear_conversation_memory(pipeline=Depends(get_pipeline)):
    """Clear LangChain conversation memory"""
    try:
        pipeline.clear_conversation_memory()
        return {"message": "Conversation memory cleared successfully"}
    except Exception as e:
        logger.error(f"Error clearing conversation memory: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clear memory: {str(e)}")


@router.get("/langchain/memory/history")
async def get_conversation_history(pipeline=Depends(get_pipeline)):
    """Get current conversation history"""
    try:
        history = pipeline.get_conversation_history()
        return {"conversation_history": history}
    except Exception as e:
        logger.error(f"Error getting conversation history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get history: {str(e)}")


# Include router in main app
def get_router() -> APIRouter:
    """Get the configured API router"""
    return router
