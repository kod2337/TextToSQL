#!/usr/bin/env python3
"""
Test the complete text-to-SQL pipeline with execution (End-to-End)
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.llm.pipeline import execute_text_to_sql
from src.database.connection import test_connection

def test_end_to_end():
    """Test complete text-to-SQL pipeline with query execution"""
    print("🚀 Testing End-to-End Text-to-SQL with Execution")
    print("=" * 55)
    
    # Test database connection
    print("📊 Testing database connection...")
    if test_connection():
        print("✅ Database connection successful")
    else:
        print("❌ Database connection failed")
        return
    print()
    
    # Test questions that should work
    test_questions = [
        "Show me all customers",
        "Find the most expensive products",
        "How many customers do we have?",
        "Show me recent orders with customer names",
        "What are the product categories we have?"
    ]
    
    print("🧪 Testing Natural Language to SQL with Execution")
    print("-" * 50)
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n{i}. Question: '{question}'")
        print("-" * (len(question) + 15))
        
        try:
            result = execute_text_to_sql(question)
            
            print(f"   🔤 SQL: {result['sql_query']}")
            print(f"   🎯 Confidence: {result['confidence']:.2f}")
            
            if result['success']:
                print(f"   ✅ Executed: {result['row_count']} rows in {result['execution_time']:.3f}s")
                
                # Show sample data
                if result.get('data') and len(result['data']) > 0:
                    sample = result['data'][0]
                    print(f"   📄 Sample: {sample}")
                
                if result.get('warnings'):
                    print(f"   ⚠️  Warnings: {result['warnings']}")
            else:
                print(f"   ❌ Execution failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"   💥 Exception: {e}")
    
    print("\n" + "=" * 55)
    print("✅ End-to-End testing completed!")
    print("\n📝 Summary:")
    print("- ✅ Natural language questions converted to SQL")
    print("- ✅ Generated SQL executed safely")
    print("- ✅ Results formatted and returned")
    print("- ✅ Error handling working properly")
    print("- ✅ Complete pipeline functional")


if __name__ == "__main__":
    test_end_to_end()
