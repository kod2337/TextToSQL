"""
LangChain integration with Groq for Text-to-SQL generation.
This replaces the custom GroqLLM implementation with proper LangChain framework.
"""

from typing import Any, List, Optional, Dict
from langchain.llms.base import LLM
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.schema import Generation, LLMResult
from groq import Groq
import logging

logger = logging.getLogger(__name__)


class GroqLangChainLLM(LLM):
    """Custom LangChain LLM wrapper for Groq API."""
    
    client: Any = None
    model_name: str = "llama-3.3-70b-versatile"  # Updated to current production model
    temperature: float = 0.1
    max_tokens: int = 1000
    
    def __init__(self, api_key: str, **kwargs):
        super().__init__(**kwargs)
        self.client = Groq(api_key=api_key)
    
    @property
    def _llm_type(self) -> str:
        return "groq"
    
    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        """Call the Groq API."""
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                stop=stop
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Groq API call failed: {e}")
            raise


class TextToSQLChain:
    """LangChain-based Text-to-SQL conversion pipeline."""
    
    def __init__(self, groq_api_key: str):
        self.llm = GroqLangChainLLM(api_key=groq_api_key)
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # SQL Generation Prompt Template
        self.sql_prompt = PromptTemplate(
            input_variables=["schema", "question"],
            template="""Generate a SQL query for this question using the provided schema.

Database Schema:
{schema}

Question: {question}

Return only the SQL query, nothing else:"""
        )
        
        # Create the chain without memory for now (simpler approach)
        self.sql_chain = LLMChain(
            llm=self.llm,
            prompt=self.sql_prompt
        )
        
        # Query Explanation Chain
        self.explain_prompt = PromptTemplate(
            input_variables=["sql_query", "question", "results"],
            template="""You are a friendly AI assistant helping with database questions. Answer naturally and conversationally.

Question: {question}
Results: {results}

Respond as if you're having a casual conversation. Focus on what the user asked about and what you found. Don't mention SQL queries, technical details, or the process - just give a natural, helpful answer about their data.

Answer:"""
        )
        
        self.explain_chain = LLMChain(
            llm=self.llm,
            prompt=self.explain_prompt
        )
    
    def generate_sql(self, question: str, schema_info: str, execution_result: Any = None) -> Dict[str, Any]:
        """Generate SQL using LangChain pipeline."""
        try:
            # Generate SQL query with simplified inputs
            sql_result = self.sql_chain.run(
                schema=schema_info,
                question=question
            )
            
            # Clean up the SQL
            sql_query = self._clean_sql_response(sql_result)
            
            # Generate natural language explanation
            results_text = "No results available"
            if execution_result and hasattr(execution_result, 'data') and execution_result.data:
                if len(execution_result.data) <= 5:
                    # Show actual data for small results
                    results_text = f"Found {len(execution_result.data)} records: {execution_result.data}"
                else:
                    # Summarize for large results
                    results_text = f"Found {len(execution_result.data)} total records. Sample: {execution_result.data[:3]}"
            elif execution_result and hasattr(execution_result, 'success') and not execution_result.success:
                results_text = f"Query execution failed: {getattr(execution_result, 'error', 'Unknown error')}"
            
            explanation = self.explain_chain.run(
                sql_query=sql_query,
                question=question,
                results=results_text
            )
            
            return {
                "sql": sql_query,
                "explanation": explanation,
                "natural_language_response": explanation,  # Add this for compatibility
                "confidence": 0.85,  # LangChain provides more reliable output
                "method": "langchain_groq"
            }
            
        except Exception as e:
            logger.error(f"LangChain SQL generation failed: {e}")
            return {
                "sql": "",
                "explanation": "I'm having trouble understanding your question. Could you try rephrasing it?",
                "natural_language_response": "I'm having trouble understanding your question. Could you try rephrasing it?",
                "confidence": 0.0,
                "method": "langchain_groq_error"
            }
    
    def _clean_sql_response(self, response: str) -> str:
        """Clean up the SQL response from LLM."""
        # Remove markdown code blocks
        response = response.replace("```sql", "").replace("```", "")
        
        # Remove common prefixes
        prefixes_to_remove = [
            "SQL Query:",
            "Query:",
            "SQL:",
            "Answer:",
        ]
        
        for prefix in prefixes_to_remove:
            if response.strip().startswith(prefix):
                response = response.replace(prefix, "", 1)
        
        return response.strip()
    
    def clear_memory(self):
        """Clear conversation memory (simplified implementation)."""
        # For now, just reset memory buffer
        self.memory.clear()
        logger.info("Conversation memory cleared")
    
    def get_conversation_history(self) -> List[str]:
        """Get conversation history (simplified implementation)."""
        # Return empty list for now since we're not using memory in chains
        return []


class LangChainSQLAgent:
    """Advanced LangChain agent for complex SQL operations."""
    
    def __init__(self, groq_api_key: str):
        self.text_to_sql = TextToSQLChain(groq_api_key)
        
        # Multi-step query template
        self.analysis_prompt = PromptTemplate(
            input_variables=["question", "schema"],
            template="""Analyze this question and break it down into steps:

Database Schema: {schema}
Question: {question}

Analysis:
1. What tables are needed?
2. What joins are required?
3. What filters/conditions?
4. What aggregations?
5. What sorting/limiting?

Step-by-step approach:"""
        )
        
        self.analysis_chain = LLMChain(
            llm=self.text_to_sql.llm,
            prompt=self.analysis_prompt
        )
    
    def analyze_complex_query(self, question: str, schema_info: str) -> Dict[str, Any]:
        """Analyze complex queries step by step."""
        try:
            analysis = self.analysis_chain.run(
                question=question,
                schema=schema_info
            )
            
            # Generate the actual SQL
            sql_result = self.text_to_sql.generate_sql(question, schema_info)
            
            return {
                **sql_result,
                "analysis": analysis,
                "method": "langchain_agent"
            }
            
        except Exception as e:
            logger.error(f"LangChain agent analysis failed: {e}")
            return {
                "sql": "",
                "explanation": "I'm having trouble with that question. Could you try asking it differently?",
                "confidence": 0.0,
                "analysis": "",
                "method": "langchain_agent_error"
            }
