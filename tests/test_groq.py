#!/usr/bin/env python3
"""
Test script for Groq integration with Text-to-SQL
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.llm.pipeline import get_text_to_sql_pipeline
from src.database.connection import test_connection
from config.settings import get_settings

def test_groq_integration():
    """Test the Groq integration"""
    print("🤖 Testing Groq Integration for Text-to-SQL")
    print("=" * 50)
    
    # Check settings
    settings = get_settings()
    print(f"Groq API Key configured: {'Yes' if settings.groq_api_key else 'No'}")
    print(f"Groq Model: {settings.groq_model}")
    print()
    
    # Test database connection
    print("📊 Testing database connection...")
    if test_connection():
        print("✅ Database connection successful")
    else:
        print("❌ Database connection failed")
        return
    print()
    
    # Initialize pipeline
    print("🔧 Initializing Text-to-SQL pipeline...")
    pipeline = get_text_to_sql_pipeline()
    print("✅ Pipeline initialized")
    print()
    
    # Test questions - including some that should really test Groq vs rule-based
    test_questions = [
        "Show me all customers",
        "Find orders from last month with customer details", 
        "What are the most expensive products?",
        "Show me customer order history with total spent",
        "Calculate total revenue from all orders",
        "List products in Electronics category sorted by price",
        "Find customers who placed orders in the last 30 days",
        "Show the top 5 customers by total spending"
    ]
    
    print("🧪 Testing SQL generation...")
    print("-" * 30)
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n{i}. Question: {question}")
        print("-" * (len(question) + 15))
        
        try:
            result = pipeline.generate_sql(question, include_metadata=True)
            
            print(f"✅ SQL: {result.query}")
            print(f"🎯 Confidence: {result.confidence:.2f}")
            
            if result.metadata:
                print(f"📝 Template: {result.metadata['template_type']}")
                if result.error:
                    print(f"⚠️  Error: {result.error}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Groq integration testing completed!")
    print("\n📝 Notes:")
    print("- If Groq API key is not configured, system falls back to rule-based generation")
    print("- To use Groq, add your API key to .env file: GROQ_API_KEY=your_key_here")
    print("- Get free API key at: https://console.groq.com/keys")
    print("- Free tier: 6,000 requests per hour")


if __name__ == "__main__":
    test_groq_integration()
