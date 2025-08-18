#!/usr/bin/env python3
"""
Quick test to verify LangChain fix
"""
import os
from dotenv import load_dotenv
from src.llm.langchain_groq import TextToSQLChain

# Load environment variables
load_dotenv()

def test_langchain():
    """Test the fixed LangChain implementation"""
    try:
        # Get API key
        groq_api_key = os.getenv('GROQ_API_KEY')
        if not groq_api_key:
            print("❌ GROQ_API_KEY not found in environment")
            return False
        
        print("🧪 Testing LangChain implementation...")
        
        # Initialize LangChain
        chain = TextToSQLChain(groq_api_key=groq_api_key)
        
        # Test schema
        test_schema = """
        Table: customers
        Columns: id, name, email, city
        
        Table: orders  
        Columns: id, customer_id, product_name, amount, order_date
        """
        
        # Test question
        test_question = "Show me all customers"
        
        print(f"📝 Question: {test_question}")
        
        # Generate SQL
        result = chain.generate_sql(test_question, test_schema)
        
        print(f"✅ SQL Generated: {result.get('sql', 'No SQL')}")
        print(f"📊 Confidence: {result.get('confidence', 0)}")
        print(f"💬 Explanation: {result.get('explanation', 'No explanation')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_langchain()
    if success:
        print("\n🎉 LangChain test passed!")
    else:
        print("\n💥 LangChain test failed!")
