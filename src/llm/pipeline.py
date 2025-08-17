"""
Text-to-SQL conversion pipeline using LangChain framework
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from src.llm.langchain_groq import TextToSQLChain, LangChainSQLAgent
from src.llm.generator import get_sql_llm
from src.llm.prompts import get_prompt_template, SchemaFormatter
from src.database.connection import get_schema_info
from src.query.executor import get_query_executor, QueryResult
from src.utils.logger import get_logger
from config.settings import get_settings

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
    """Main pipeline for converting text to SQL using LangChain"""
    
    def __init__(self):
        settings = get_settings()
        
        # Initialize LangChain components
        self.langchain_sql = TextToSQLChain(groq_api_key=settings.groq_api_key)
        self.langchain_agent = LangChainSQLAgent(groq_api_key=settings.groq_api_key)
        
        # Fallback to custom LLM if needed
        self.fallback_llm = get_sql_llm()
        
        self.schema_formatter = SchemaFormatter()
        self.query_executor = get_query_executor()
        self._cached_schema = None
        
        logger.info("Text-to-SQL pipeline initialized with LangChain and query executor")
    
    def get_schema_context(self) -> Dict[str, Any]:
        """Get database schema context (cached)"""
        if self._cached_schema is None:
            self._cached_schema = get_schema_info()
            logger.info(f"Schema loaded: {len(self._cached_schema)} tables")
        return self._cached_schema
    
    def generate_sql(
        self, 
        question: str, 
        template_type: str = "langchain",
        include_metadata: bool = False,
        execute_query: bool = False,
        use_agent: bool = False
    ) -> SQLGenerationResult:
        """
        Generate SQL from natural language question using LangChain
        
        Args:
            question: Natural language question
            template_type: "langchain" for LangChain, "few_shot" for custom
            include_metadata: Whether to include generation metadata
            execute_query: Whether to execute the generated query
            use_agent: Whether to use LangChain agent for complex analysis
            
        Returns:
            SQLGenerationResult with generated query and optional execution result
        """
        try:
            logger.info(f"Generating SQL for question: {question}")
            
            # Get schema information
            schema_info = self.get_schema_context()
            formatted_schema = self.schema_formatter.format_schema_info(schema_info)
            
            # Use LangChain for SQL generation
            if template_type == "langchain" or use_agent:
                if use_agent:
                    logger.info("Using LangChain agent for complex query analysis")
                    result = self.langchain_agent.analyze_complex_query(question, formatted_schema)
                else:
                    logger.info("Using LangChain TextToSQLChain")
                    
                    # First generate SQL
                    initial_result = self.langchain_sql.generate_sql(question, formatted_schema)
                    sql_query = initial_result.get("sql", "")
                    
                    # Execute query if requested to get real results
                    execution_result = None
                    if execute_query and sql_query:
                        logger.info("Executing generated SQL query for LangChain analysis")
                        execution_result = self.query_executor.execute_query(sql_query)
                        
                        # Generate enhanced explanation with actual results
                        enhanced_result = self.langchain_sql.generate_sql(question, formatted_schema, execution_result)
                        result = enhanced_result
                        
                        # Make sure we keep the execution result
                        result["execution_result"] = execution_result
                    else:
                        # No execution, use initial result
                        result = initial_result
                
                sql_query = result.get("sql", "")
                confidence = result.get("confidence", 0.0)
                
                # Prepare metadata
                metadata = None
                if include_metadata:
                    metadata = {
                        "method": result.get("method", "langchain"),
                        "template_type": template_type,
                        "schema_tables": list(schema_info.keys()),
                        "langchain_explanation": result.get("explanation", ""),
                        "natural_language_response": result.get("natural_language_response", ""),
                        "use_agent": use_agent
                    }
                    
                    if "analysis" in result:
                        metadata["agent_analysis"] = result["analysis"]
                
            else:
                # Fallback to custom implementation
                logger.info("Using custom LLM implementation")
                template = get_prompt_template(template_type)
                prompt_vars = {
                    "question": question,
                    "schema_info": formatted_schema
                }
                prompt = template.format(**prompt_vars)
                sql_query = self.fallback_llm.generate_sql(prompt, schema_info)
                confidence = self._calculate_confidence(sql_query, question)
                
                metadata = None
                if include_metadata:
                    metadata = {
                        "method": "custom_llm",
                        "template_type": template_type,
                        "schema_tables": list(schema_info.keys()),
                        "prompt_length": len(prompt),
                        "use_agent": False
                    }
            
            # Clean up the generated SQL
            cleaned_query = self._clean_sql_query(sql_query)
            
            # Get execution result from LangChain result or execute if needed
            execution_result = None
            if execute_query and cleaned_query:
                if "execution_result" in result:
                    # Use execution result from LangChain
                    execution_result = result["execution_result"]
                    logger.info("Using execution result from LangChain")
                else:
                    # Execute query ourselves
                    logger.info("Executing generated SQL query")
                    execution_result = self.query_executor.execute_query(cleaned_query)
            
            result = SQLGenerationResult(
                query=cleaned_query,
                confidence=confidence,
                prompt_used="",  # LangChain handles prompting internally
                execution_result=execution_result,
                metadata=metadata
            )
            
            logger.info(f"SQL generated successfully with LangChain: {cleaned_query}")
            return result
            
        except Exception as e:
            logger.error(f"Error generating SQL with LangChain: {e}")
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
    
    def clear_conversation_memory(self):
        """Clear LangChain conversation memory"""
        self.langchain_sql.clear_memory()
        logger.info("Conversation memory cleared")
    
    def get_conversation_history(self) -> List[str]:
        """Get current conversation history"""
        return self.langchain_sql.get_conversation_history()
    
    def generate_sql_with_context(self, question: str, execute_query: bool = False) -> SQLGenerationResult:
        """
        Generate SQL with conversation context (simplified interface)
        
        Args:
            question: Natural language question
            execute_query: Whether to execute the generated query
            
        Returns:
            SQLGenerationResult with LangChain-generated query
        """
        return self.generate_sql(
            question=question,
            template_type="langchain",
            include_metadata=True,
            execute_query=execute_query,
            use_agent=False
        )
    
    def analyze_complex_question(self, question: str, execute_query: bool = False) -> SQLGenerationResult:
        """
        Analyze complex questions using LangChain agent
        
        Args:
            question: Natural language question
            execute_query: Whether to execute the generated query
            
        Returns:
            SQLGenerationResult with agent analysis and query
        """
        return self.generate_sql(
            question=question,
            template_type="langchain",
            include_metadata=True,
            execute_query=execute_query,
            use_agent=True
        )
    
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
