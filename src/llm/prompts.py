"""
Prompt templates for text-to-SQL conversion
"""
from typing import Dict, Any, List
from dataclasses import dataclass
from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class PromptTemplate:
    """Template for SQL generation prompts"""
    template: str
    input_variables: List[str]
    
    def format(self, **kwargs) -> str:
        """Format the template with provided variables"""
        try:
            return self.template.format(**kwargs)
        except KeyError as e:
            logger.error(f"Missing template variable: {e}")
            return ""


class SQLPromptTemplates:
    """Collection of prompt templates for SQL generation"""
    
    @staticmethod
    def get_basic_sql_prompt() -> PromptTemplate:
        """Basic text-to-SQL prompt template"""
        template = """
You are an expert SQL query generator. Given a database schema and a natural language question, generate a valid SQL query.

Database Schema:
{schema_info}

Question: {question}

Instructions:
1. Generate only the SQL query, no explanations
2. Use proper SQL syntax for PostgreSQL
3. Include appropriate JOINs when querying multiple tables
4. Use proper column and table names from the schema
5. Add appropriate WHERE clauses and ORDER BY when needed
6. End the query with a semicolon

SQL Query:
"""
        return PromptTemplate(
            template=template,
            input_variables=["schema_info", "question"]
        )
    
    @staticmethod
    def get_schema_aware_prompt() -> PromptTemplate:
        """Schema-aware prompt with detailed table information"""
        template = """
You are a SQL expert. Convert the natural language question to a SQL query using the provided database schema.

=== DATABASE SCHEMA ===
{detailed_schema}

=== RELATIONSHIPS ===
{relationships}

=== SAMPLE DATA ===
{sample_data}

=== QUESTION ===
{question}

=== INSTRUCTIONS ===
1. Use only tables and columns that exist in the schema
2. Use proper PostgreSQL syntax
3. Include JOINs when data from multiple tables is needed
4. Use appropriate WHERE clauses for filtering
5. Add ORDER BY for better result presentation
6. Return only the SQL query, nothing else

=== SQL QUERY ===
"""
        return PromptTemplate(
            template=template,
            input_variables=["detailed_schema", "relationships", "sample_data", "question"]
        )
    
    @staticmethod
    def get_few_shot_prompt() -> PromptTemplate:
        """Few-shot learning prompt with examples"""
        template = """
You are an expert SQL generator. Here are some examples of converting natural language questions to SQL queries:

=== DATABASE SCHEMA ===
{schema_info}

=== EXAMPLES ===
Question: Show me all customers
SQL: SELECT * FROM customers;

Question: Find orders from the last 30 days
SQL: SELECT o.*, c.first_name, c.last_name FROM orders o JOIN customers c ON o.customer_id = c.id WHERE o.order_date >= CURRENT_DATE - INTERVAL '30 days' ORDER BY o.order_date DESC;

Question: What are the top 5 most expensive products?
SQL: SELECT * FROM products ORDER BY price DESC LIMIT 5;

Question: Show total revenue by month
SQL: SELECT DATE_TRUNC('month', order_date) as month, SUM(total_amount) as revenue FROM orders GROUP BY DATE_TRUNC('month', order_date) ORDER BY month DESC;

=== NEW QUESTION ===
Question: {question}
SQL: """
        return PromptTemplate(
            template=template,
            input_variables=["schema_info", "question"]
        )


class SchemaFormatter:
    """Format database schema information for prompts"""
    
    @staticmethod
    def format_schema_info(schema_info: Dict[str, Any]) -> str:
        """Format schema information as readable text"""
        formatted = "Tables and Columns:\n"
        
        for table_name, table_info in schema_info.items():
            formatted += f"\n{table_name}:\n"
            for column in table_info['columns']:
                nullable = "NULL" if column['nullable'] else "NOT NULL"
                default = f" DEFAULT {column['default']}" if column['default'] else ""
                formatted += f"  - {column['name']} ({column['type']}) {nullable}{default}\n"
        
        return formatted
    
    @staticmethod
    def format_detailed_schema(schema_info: Dict[str, Any]) -> str:
        """Format detailed schema with descriptions"""
        formatted = ""
        
        for table_name, table_info in schema_info.items():
            formatted += f"\nTable: {table_name}\n"
            formatted += "Columns:\n"
            
            for column in table_info['columns']:
                col_info = f"  {column['name']} - {column['type']}"
                if not column['nullable']:
                    col_info += " (required)"
                if column['default']:
                    col_info += f" default: {column['default']}"
                formatted += col_info + "\n"
        
        return formatted
    
    @staticmethod
    def format_relationships() -> str:
        """Format table relationships"""
        return """
Table Relationships:
- customers.id → orders.customer_id (one-to-many)
- orders.id → order_items.order_id (one-to-many)
- products.id → order_items.product_id (one-to-many)
"""
    
    @staticmethod
    def format_sample_data() -> str:
        """Format sample data examples"""
        return """
Sample Data Insights:
- customers: Contains customer information (names, email, addresses)
- products: Contains product catalog (electronics, furniture categories)
- orders: Contains order information with status (pending, processing, delivered, cancelled)
- order_items: Contains individual items within each order

Common Query Patterns:
- Customer orders: JOIN customers and orders
- Order details: JOIN orders, order_items, and products
- Sales analysis: SUM(total_amount) from orders
- Product analysis: GROUP BY category from products
"""


def get_prompt_template(template_type: str = "basic") -> PromptTemplate:
    """
    Get a prompt template by type
    
    Args:
        template_type: Type of template ('basic', 'schema_aware', 'few_shot')
        
    Returns:
        PromptTemplate instance
    """
    templates = SQLPromptTemplates()
    
    if template_type == "basic":
        return templates.get_basic_sql_prompt()
    elif template_type == "schema_aware":
        return templates.get_schema_aware_prompt()
    elif template_type == "few_shot":
        return templates.get_few_shot_prompt()
    else:
        logger.warning(f"Unknown template type: {template_type}, using basic")
        return templates.get_basic_sql_prompt()
