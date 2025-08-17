"""
Text-to-SQL conversion pipeline
"""
from typing import Dict, Any, Optional
from dataclasses import dataclass
from src.llm.generator import get_sql_llm
from src.llm.prompts import get_prompt_template, SchemaFormatter
from src.database.connection import get_schema_info
from src.query.executor import get_query_executor, QueryResult
from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class SQLGenerationResult:
    """Result of SQL generation and execution"""
    query: str
    confidence: float
    prompt_used: str
    execution_result: Optional[QueryResult] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class TextToSQLPipeline:
    """Main pipeline for converting text to SQL"""
    
    def __init__(self):
        self.llm = get_sql_llm()
        self.schema_formatter = SchemaFormatter()
        self.query_executor = get_query_executor()
        self._cached_schema = None
        
        logger.info("Text-to-SQL pipeline initialized with query executor")
    
    def get_schema_context(self) -> Dict[str, Any]:
        """Get database schema context (cached)"""
        if self._cached_schema is None:
            self._cached_schema = get_schema_info()
            logger.info(f"Schema loaded: {len(self._cached_schema)} tables")
        return self._cached_schema
    
    def generate_sql(
        self, 
        question: str, 
        template_type: str = "few_shot",
        include_metadata: bool = False,
        execute_query: bool = False
    ) -> SQLGenerationResult:
        """
        Generate SQL from natural language question
        
        Args:
            question: Natural language question
            template_type: Type of prompt template to use
            include_metadata: Whether to include generation metadata
            execute_query: Whether to execute the generated query
            
        Returns:
            SQLGenerationResult with generated query and optional execution result
        """
        try:
            logger.info(f"Generating SQL for question: {question}")
            
            # Get schema information
            schema_info = self.get_schema_context()
            
            # Format schema for prompt
            formatted_schema = self.schema_formatter.format_schema_info(schema_info)
            
            # Get prompt template
            template = get_prompt_template(template_type)
            
            # Prepare prompt variables
            prompt_vars = {"question": question}
            
            if template_type == "basic":
                prompt_vars["schema_info"] = formatted_schema
            elif template_type == "schema_aware":
                prompt_vars.update({
                    "detailed_schema": self.schema_formatter.format_detailed_schema(schema_info),
                    "relationships": self.schema_formatter.format_relationships(),
                    "sample_data": self.schema_formatter.format_sample_data()
                })
            elif template_type == "few_shot":
                prompt_vars["schema_info"] = formatted_schema
            
            # Format prompt
            prompt = template.format(**prompt_vars)
            
            # Generate SQL
            sql_query = self.llm.generate_sql(prompt, schema_info)
            
            # Clean up the generated SQL
            cleaned_query = self._clean_sql_query(sql_query)
            
            # Calculate confidence (simple heuristic for now)
            confidence = self._calculate_confidence(cleaned_query, question)
            
            # Prepare metadata
            metadata = None
            if include_metadata:
                metadata = {
                    "template_type": template_type,
                    "schema_tables": list(schema_info.keys()),
                    "prompt_length": len(prompt),
                    "raw_query": sql_query
                }
            
            # Execute query if requested
            execution_result = None
            if execute_query and cleaned_query:
                logger.info("Executing generated SQL query")
                execution_result = self.query_executor.execute_query(cleaned_query)
            
            result = SQLGenerationResult(
                query=cleaned_query,
                confidence=confidence,
                prompt_used=prompt if include_metadata else "",
                execution_result=execution_result,
                metadata=metadata
            )
            
            logger.info(f"SQL generated successfully: {cleaned_query}")
            return result
            
        except Exception as e:
            logger.error(f"Error generating SQL: {e}")
            return SQLGenerationResult(
                query="",
                confidence=0.0,
                prompt_used="",
                execution_result=None,
                error=str(e)
            )
    
    def _clean_sql_query(self, query: str) -> str:
        """Clean and format the generated SQL query"""
        if not query:
            return ""
        
        # Remove extra whitespace
        query = query.strip()
        
        # Ensure query ends with semicolon
        if not query.endswith(';'):
            query += ';'
        
        # Remove any markdown code blocks
        if query.startswith('```'):
            lines = query.split('\n')
            query = '\n'.join(lines[1:-1] if lines[-1].strip() == '```' else lines[1:])
            query = query.strip()
        
        # Remove common prefixes
        prefixes_to_remove = [
            "SQL:",
            "Query:",
            "SELECT:",
            "sql:",
            "query:"
        ]
        
        for prefix in prefixes_to_remove:
            if query.startswith(prefix):
                query = query[len(prefix):].strip()
        
        return query
    
    def _calculate_confidence(self, query: str, question: str) -> float:
        """Calculate confidence score for the generated query"""
        if not query or query == "SELECT * FROM customers LIMIT 5;":
            return 0.3  # Low confidence for fallback queries
        
        confidence = 0.5  # Base confidence
        
        # Boost confidence for certain patterns
        question_lower = question.lower()
        query_lower = query.lower()
        
        # Check for relevant keywords
        if "customer" in question_lower and "customers" in query_lower:
            confidence += 0.2
        if "order" in question_lower and "orders" in query_lower:
            confidence += 0.2
        if "product" in question_lower and "products" in query_lower:
            confidence += 0.2
        
        # Check for proper SQL structure
        if "join" in query_lower and ("join" in question_lower or "with" in question_lower):
            confidence += 0.1
        if "where" in query_lower and any(word in question_lower for word in ["where", "filter", "find", "get"]):
            confidence += 0.1
        if "order by" in query_lower and any(word in question_lower for word in ["sort", "order", "arrange"]):
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def test_pipeline(self) -> Dict[str, Any]:
        """Test the pipeline with sample questions"""
        test_questions = [
            "Show me all customers",
            "Find orders from last month",
            "What are the most expensive products?",
            "Show me customer order history",
            "Calculate total revenue"
        ]
        
        results = {}
        for question in test_questions:
            try:
                result = self.generate_sql(question)
                results[question] = {
                    "query": result.query,
                    "confidence": result.confidence,
                    "success": bool(result.query and not result.error)
                }
            except Exception as e:
                results[question] = {
                    "query": "",
                    "confidence": 0.0,
                    "success": False,
                    "error": str(e)
                }
        
        return results


# Global pipeline instance
_pipeline_instance = None


def get_text_to_sql_pipeline() -> TextToSQLPipeline:
    """Get the global text-to-SQL pipeline instance"""
    global _pipeline_instance
    if _pipeline_instance is None:
        _pipeline_instance = TextToSQLPipeline()
    return _pipeline_instance


def generate_sql_from_text(question: str, template_type: str = "few_shot") -> str:
    """
    Simple function to generate SQL from text
    
    Args:
        question: Natural language question
        template_type: Prompt template type
        
    Returns:
        Generated SQL query
    """
    pipeline = get_text_to_sql_pipeline()
    result = pipeline.generate_sql(question, template_type)
    return result.query


def execute_text_to_sql(question: str, template_type: str = "few_shot") -> Dict[str, Any]:
    """
    Generate SQL from text and execute it safely
    
    Args:
        question: Natural language question
        template_type: Prompt template type
        
    Returns:
        Complete result with SQL, execution data, and metadata
    """
    pipeline = get_text_to_sql_pipeline()
    result = pipeline.generate_sql(
        question, 
        template_type=template_type, 
        include_metadata=True, 
        execute_query=True
    )
    
    response = {
        "question": question,
        "sql_query": result.query,
        "confidence": result.confidence,
        "success": result.execution_result.success if result.execution_result else False
    }
    
    if result.execution_result:
        response.update({
            "data": result.execution_result.data,
            "row_count": result.execution_result.row_count,
            "execution_time": result.execution_result.execution_time
        })
        
        if result.execution_result.warnings:
            response["warnings"] = result.execution_result.warnings
        
        if not result.execution_result.success:
            response["error"] = result.execution_result.error
    
    if result.error:
        response["sql_generation_error"] = result.error
    
    if result.metadata:
        response["metadata"] = result.metadata
    
    return response
