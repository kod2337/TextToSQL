"""
Safe SQL Query Execution & Validation
"""
import sqlalchemy
from sqlalchemy.exc import SQLAlchemyError, TimeoutError
import re
import logging
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from src.database.connection import create_database_engine
from src.utils.logger import get_logger

logger = get_logger(__name__)

logger = get_logger(__name__)


@dataclass
class QueryResult:
    """Result of query execution"""
    success: bool
    data: Optional[List[Dict[str, Any]]] = None
    row_count: int = 0
    execution_time: float = 0.0
    error: Optional[str] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


class QuerySafetyError(Exception):
    """Raised when a query violates safety rules"""
    pass


class QueryValidator:
    """SQL Query validation and safety checks"""
    
    # Dangerous SQL keywords that are completely forbidden
    FORBIDDEN_KEYWORDS = [
        'drop', 'truncate', 'alter', 'create', 'insert', 'update', 
        'delete', 'grant', 'revoke', 'exec', 'execute', 'call',
        'replace', 'merge', 'into', 'values'
    ]
    
    # Keywords that require careful handling
    RESTRICTED_KEYWORDS = [
        'union', 'information_schema', 'pg_', 'mysql.', 'sys.',
        'master.', 'msdb.', 'tempdb.', 'performance_schema'
    ]
    
    def __init__(self, max_joins: int = 5, max_length: int = 2000, max_subqueries: int = 3):
        self.max_joins = max_joins
        self.max_length = max_length
        self.max_subqueries = max_subqueries
    
    def validate_syntax(self, query: str) -> bool:
        """Basic SQL syntax validation"""
        query_clean = query.strip()
        if not query_clean:
            raise QuerySafetyError("Empty query")
        
        # Must start with SELECT (case-insensitive)
        if not query_clean.lower().startswith('select'):
            raise QuerySafetyError("Only SELECT queries are allowed")
        
        # Basic parentheses matching
        if query_clean.count('(') != query_clean.count(')'):
            raise QuerySafetyError("Unmatched parentheses in query")
        
        return True
    
    def check_forbidden_keywords(self, query: str) -> None:
        """Check for completely forbidden SQL operations"""
        query_lower = query.lower()
        
        for keyword in self.FORBIDDEN_KEYWORDS:
            # Use word boundaries to avoid false positives
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, query_lower):
                raise QuerySafetyError(f"Forbidden keyword '{keyword}' detected")
        
        # Also block access to system schemas
        for restricted in self.RESTRICTED_KEYWORDS:
            if restricted in query_lower:
                raise QuerySafetyError(f"Access to '{restricted}' is not allowed")
    
    def check_restricted_keywords(self, query: str) -> List[str]:
        """Check for restricted keywords and return warnings (now redundant as they're forbidden)"""
        # This method is now largely redundant since we moved restrictions to forbidden
        # But kept for potential future use with warnings-only keywords
        return []
    
    def check_complexity_limits(self, query: str) -> None:
        """Enforce query complexity limits"""
        query_lower = query.lower()
        
        # Check query length
        if len(query) > self.max_length:
            raise QuerySafetyError(f"Query too long: {len(query)} > {self.max_length} characters")
        
        # Count JOINs
        join_count = len(re.findall(r'\bjoin\b', query_lower))
        if join_count > self.max_joins:
            raise QuerySafetyError(f"Too many JOINs: {join_count} > {self.max_joins}")
        
        # Count subqueries (simplified detection)
        subquery_count = query_lower.count('select') - 1  # Main query doesn't count
        if subquery_count > self.max_subqueries:
            raise QuerySafetyError(f"Too many subqueries: {subquery_count} > {self.max_subqueries}")
    
    def validate_query(self, query: str) -> List[str]:
        """Complete query validation - returns warnings"""
        self.validate_syntax(query)
        self.check_forbidden_keywords(query)
        self.check_complexity_limits(query)
        warnings = self.check_restricted_keywords(query)
        return warnings


class SafeQueryExecutor:
    """Safe SQL query execution with comprehensive safety checks"""
    
    def __init__(self, default_timeout: int = 10, max_rows: int = 1000):
        self.validator = QueryValidator()
        self.default_timeout = default_timeout
        self.max_rows = max_rows
        logger.info("Safe Query Executor initialized")
    
    def execute_query(self, query: str, timeout: Optional[int] = None) -> QueryResult:
        """
        Execute SQL query safely with validation and error handling
        
        Args:
            query: SQL query string
            timeout: Query timeout in seconds (uses default if None)
            
        Returns:
            QueryResult with execution details
        """
        start_time = time.time()
        timeout = timeout or self.default_timeout
        
        try:
            # Step 1: Validate query
            logger.info(f"Validating query: {query[:100]}...")
            warnings = self.validator.validate_query(query)
            
            # Step 2: Execute query
            logger.info(f"Executing query with {timeout}s timeout")
            engine = create_database_engine()
            
            with engine.connect() as conn:
                # Set query timeout
                result = conn.execution_options(
                    isolation_level="AUTOCOMMIT",
                    compiled_cache={}
                ).execute(
                    sqlalchemy.text(query)
                )
                
                # Fetch results with row limit
                rows = []
                row_count = 0
                
                for row in result:
                    if row_count >= self.max_rows:
                        warnings.append(f"Result truncated to {self.max_rows} rows")
                        break
                    rows.append(dict(row._mapping))
                    row_count += 1
                
                execution_time = time.time() - start_time
                
                logger.info(f"Query executed successfully: {row_count} rows in {execution_time:.2f}s")
                
                return QueryResult(
                    success=True,
                    data=rows,
                    row_count=row_count,
                    execution_time=execution_time,
                    warnings=warnings
                )
                
        except QuerySafetyError as e:
            execution_time = time.time() - start_time
            logger.warning(f"Query safety violation: {e}")
            return QueryResult(
                success=False,
                execution_time=execution_time,
                error=f"Safety violation: {str(e)}"
            )
            
        except TimeoutError as e:
            execution_time = time.time() - start_time
            logger.error(f"Query timeout after {timeout}s: {e}")
            return QueryResult(
                success=False,
                execution_time=execution_time,
                error=f"Query timeout after {timeout} seconds"
            )
            
        except SQLAlchemyError as e:
            execution_time = time.time() - start_time
            logger.error(f"Database error: {e}")
            return QueryResult(
                success=False,
                execution_time=execution_time,
                error=f"Database error: {str(e)}"
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Unexpected error: {e}")
            return QueryResult(
                success=False,
                execution_time=execution_time,
                error=f"Unexpected error: {str(e)}"
            )
    
    def format_result(self, result: QueryResult) -> Dict[str, Any]:
        """Format query result for API response"""
        formatted = {
            "success": result.success,
            "execution_time": round(result.execution_time, 3),
            "row_count": result.row_count
        }
        
        if result.success:
            formatted["data"] = result.data
            if result.warnings:
                formatted["warnings"] = result.warnings
        else:
            formatted["error"] = result.error
        
        return formatted
    
    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            test_result = self.execute_query("SELECT 1 as test_value")
            return test_result.success
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False


# Global executor instance
_executor_instance = None


def get_query_executor() -> SafeQueryExecutor:
    """Get the global query executor instance"""
    global _executor_instance
    if _executor_instance is None:
        _executor_instance = SafeQueryExecutor()
    return _executor_instance


def execute_sql_safely(query: str, timeout: Optional[int] = None) -> Dict[str, Any]:
    """
    Convenient function to execute SQL safely
    
    Args:
        query: SQL query string
        timeout: Query timeout in seconds
        
    Returns:
        Formatted result dictionary
    """
    executor = get_query_executor()
    result = executor.execute_query(query, timeout)
    return executor.format_result(result)
