"""
LLM integration for text-to-SQL conversion
"""
from typing import Optional, Dict, Any
import os
from langchain.llms.base import LLM
from langchain.callbacks.manager import CallbackManagerForLLMRun
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch
from groq import Groq
from config.settings import get_settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


class GroqLLM:
    """
    Groq LLM integration for fast text-to-SQL generation
    """
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        settings = get_settings()
        self.api_key = api_key or settings.groq_api_key
        self.model = model or settings.groq_model
        self.client = None
        
        if self.api_key:
            try:
                self.client = Groq(api_key=self.api_key)
                logger.info(f"Groq client initialized with model: {self.model}")
            except Exception as e:
                logger.error(f"Failed to initialize Groq client: {e}")
                self.client = None
        else:
            logger.warning("No Groq API key provided")
    
    def is_available(self) -> bool:
        """Check if Groq is available and configured"""
        return self.client is not None
    
    def generate_sql(self, prompt: str, schema_info: Dict[str, Any]) -> str:
        """
        Generate SQL using Groq API only (no rule-based fallback)
        """
        if not self.is_available():
            logger.error("Groq API is not available. Please check your API key.")
            raise RuntimeError("Groq API is not available. Please check your API key.")
        try:
            settings = get_settings()
            sql_prompt = self._create_sql_focused_prompt(prompt)
            logger.info(f"Sending prompt to Groq: {sql_prompt[:200]}...")
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert SQL query generator. Given a database schema and a natural language question, generate ONLY the SQL query. Do not include explanations, markdown, or any other text. Return only the SQL query that would answer the question."
                    },
                    {
                        "role": "user", 
                        "content": sql_prompt
                    }
                ],
                model=self.model,
                temperature=settings.temperature,
                max_tokens=settings.max_tokens,
                stop=["```", "\n\n", "Explanation:", "Note:"]
            )
            sql_query = chat_completion.choices[0].message.content.strip()
            logger.info(f"Groq generated SQL: {sql_query}")
            cleaned = self._clean_groq_response(sql_query)
            logger.info(f"Cleaned SQL: {cleaned}")
            return cleaned
        except Exception as e:
            logger.error(f"Error with Groq API: {e}")
            logger.exception("Full error details:")
            raise
    
    def _create_sql_focused_prompt(self, original_prompt: str) -> str:
        """Create a focused prompt optimized for Groq"""
        # Extract the question from the original prompt
        question = self._extract_question_from_prompt(original_prompt)
        logger.info(f"Extracted question for Groq: '{question}'")
        
        # Create a cleaner, more focused prompt
        sql_prompt = f"""Database Schema:
Tables:
1. customers: id (primary key), first_name, last_name, email, phone, created_at
2. products: id (primary key), name, description, price, category, stock_quantity  
3. orders: id (primary key), customer_id (foreign key to customers.id), order_date, total_amount
4. order_items: id (primary key), order_id (foreign key to orders.id), product_id (foreign key to products.id), quantity, price

Sample queries:
- "show all customers" → SELECT * FROM customers;
- "find recent orders" → SELECT o.*, c.first_name, c.last_name FROM orders o JOIN customers c ON o.customer_id = c.id WHERE o.order_date >= CURRENT_DATE - INTERVAL '30 days';
- "expensive products" → SELECT * FROM products ORDER BY price DESC LIMIT 10;
- "customer order history" → SELECT c.first_name, c.last_name, COUNT(o.id) as order_count FROM customers c LEFT JOIN orders o ON c.id = o.customer_id GROUP BY c.id, c.first_name, c.last_name;

Question: {question}

SQL Query:"""
        
        return sql_prompt
    
    def _clean_groq_response(self, response: str) -> str:
        """Clean up Groq API response"""
        if not response:
            return ""
        
        # Remove common prefixes/suffixes
        response = response.strip()
        
        # Remove markdown code blocks
        if response.startswith('```sql'):
            response = response[6:]
        elif response.startswith('```'):
            response = response[3:]
        
        if response.endswith('```'):
            response = response[:-3]
        
        # Remove common prefixes
        prefixes = ["SQL:", "Query:", "SELECT:", "sql:", "query:"]
        for prefix in prefixes:
            if response.startswith(prefix):
                response = response[len(prefix):].strip()
        
        # Ensure it ends with semicolon
        response = response.strip()
        if response and not response.endswith(';'):
            response += ';'
        
        return response
    
    # Rule-based fallback removed. Only prompt-based Groq generation is used.
    
    def _extract_question_from_prompt(self, prompt: str) -> str:
        """Extract the actual question from the structured prompt"""
        lines = prompt.strip().split('\n')
        # Look for "=== NEW QUESTION ===" section and get the first "Question:" after it
        for i, line in enumerate(lines):
            if "=== NEW QUESTION ===" in line:
                for j in range(i + 1, len(lines)):
                    if lines[j].strip().startswith("Question:"):
                        question = lines[j].replace("Question:", "").strip()
                        logger.info(f"Extracted user question after NEW QUESTION marker: '{question}'")
                        return question
        # If no NEW QUESTION marker, get the last "Question:" line
        all_questions = [line.replace("Question:", "").strip() for line in lines if line.strip().startswith("Question:")]
        if all_questions:
            question = all_questions[-1]
            logger.info(f"Extracted last question in prompt: '{question}'")
            return question
        # Fallback
        logger.warning(f"Could not extract question from prompt: {prompt[:200]}...")
        return "show me all customers"


class LocalLLM(LLM):
    """
    Custom LangChain LLM wrapper for local Hugging Face models
    """
    
    model_name: str = "microsoft/DialoGPT-medium"
    tokenizer: Any = None
    model: Any = None
    pipeline: Any = None
    
    def __init__(self, model_name: Optional[str] = None):
        super().__init__()
        settings = get_settings()
        self.model_name = model_name or settings.llm_model_name
        self._load_model()
    
    def _load_model(self):
        """Load the model and tokenizer"""
        try:
            logger.info(f"Loading model: {self.model_name}")
            
            # Check if CUDA is available
            device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"Using device: {device}")
            
            # Load tokenizer and model
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16 if device == "cuda" else torch.float32,
                device_map="auto" if device == "cuda" else None
            )
            
            # Add padding token if not present
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Create text generation pipeline
            self.pipeline = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                device=0 if device == "cuda" else -1,
                torch_dtype=torch.float16 if device == "cuda" else torch.float32,
            )
            
            logger.info(f"Model {self.model_name} loaded successfully on {device}")
            
        except Exception as e:
            logger.error(f"Failed to load model {self.model_name}: {e}")
            raise
    
    @property
    def _llm_type(self) -> str:
        """Return identifier of llm type."""
        return "local_huggingface"
    
    def _call(
        self,
        prompt: str,
        stop: Optional[list[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Generate text from the model"""
        try:
            settings = get_settings()
            
            # Generate text
            outputs = self.pipeline(
                prompt,
                max_new_tokens=settings.max_tokens,
                temperature=settings.temperature,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
                stop_sequence=stop,
                return_full_text=False
            )
            
            # Extract generated text
            generated_text = outputs[0]['generated_text'].strip()
            
            # Apply stop sequences if provided
            if stop:
                for stop_seq in stop:
                    if stop_seq in generated_text:
                        generated_text = generated_text.split(stop_seq)[0].strip()
            
            return generated_text
            
        except Exception as e:
            logger.error(f"Error generating text: {e}")
            return ""


class SQLGenerationLLM:
    """
    Specialized LLM for SQL generation
    Uses Groq API for fast inference with rule-based fallback
    """
    
    def __init__(self):
        self.groq_llm = GroqLLM()
        logger.info("SQL Generation LLM initialized with Groq integration")
    
    def generate_sql(self, prompt: str, schema_info: Dict[str, Any]) -> str:
        """
        Generate SQL from natural language prompt using Groq API only.
        """
        if not self.groq_llm.is_available():
            logger.error("Groq API is not available. Please check your API key.")
            raise RuntimeError("Groq API is not available. Please check your API key.")
        return self.groq_llm.generate_sql(prompt, schema_info)
    
    # Rule-based generation removed. Only Groq prompt-based generation is used.
    
    def _extract_question_from_prompt(self, prompt: str) -> str:
        """Extract the actual question from the structured prompt"""
        lines = prompt.strip().split('\n')
        
        # Method 1: Look for "=== NEW QUESTION ===" section and get the Question: after it
        for i, line in enumerate(lines):
            if "=== NEW QUESTION ===" in line:
                # Look for the next "Question:" line after this marker
                for j in range(i + 1, len(lines)):
                    if lines[j].strip().startswith("Question:"):
                        question = lines[j].replace("Question:", "").strip()
                        logger.info(f"Found question after NEW QUESTION marker: '{question}'")
                        return question
        
        # Method 2: If no NEW QUESTION marker, get the LAST "Question:" line
        all_questions = []
        for line in lines:
            if line.strip().startswith("Question:"):
                question = line.replace("Question:", "").strip()
                all_questions.append(question)
        
        if all_questions:
            last_question = all_questions[-1]
            logger.info(f"Found last question from {len(all_questions)} questions: '{last_question}'")
            return last_question
        
        # Method 3: If it's a simple direct question without template structure
        prompt_clean = prompt.strip()
        if len(prompt_clean.split('\n')) <= 3 and not '===' in prompt_clean:
            logger.info(f"Direct question detected: '{prompt_clean}'")
            return prompt_clean
        
        # Fallback: return a default
        logger.warning(f"Could not extract question from prompt: {prompt[:200]}...")
        return "show me all customers"


def get_sql_llm() -> SQLGenerationLLM:
    """Get SQL generation LLM instance"""
    return SQLGenerationLLM()
