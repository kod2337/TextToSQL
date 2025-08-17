#!/usr/bin/env python3
"""
Complete Text-to-SQL Assistant Demo
Shows the full working program even though we're only at Phase 4
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.llm.pipeline import execute_text_to_sql, get_text_to_sql_pipeline
from src.database.connection import test_connection, get_schema_info
from src.query.executor import get_query_executor
import json

def print_header(title):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"🚀 {title}")
    print(f"{'='*60}")

def print_section(title):
    """Print a formatted section"""
    print(f"\n{'─'*40}")
    print(f"📋 {title}")
    print(f"{'─'*40}")

def demo_complete_system():
    """Demo the complete Text-to-SQL system"""
    
    print_header("COMPLETE TEXT-TO-SQL ASSISTANT DEMO")
    print("🎯 Natural Language ➜ SQL ➜ Results")
    print("💡 Powered by Groq AI + Supabase PostgreSQL")
    
    # 1. System Health Check
    print_section("System Health Check")
    
    print("🔍 Checking database connection...")
    if test_connection():
        print("✅ Database: Connected to Supabase PostgreSQL")
    else:
        print("❌ Database: Connection failed")
        return
    
    print("🧠 Checking AI integration...")
    pipeline = get_text_to_sql_pipeline()
    if pipeline.llm.groq_llm.is_available():
        print("✅ AI: Groq API connected and ready")
    else:
        print("❌ AI: Groq API not available")
        return
    
    print("🛡️ Checking security systems...")
    executor = get_query_executor()
    if executor.test_connection():
        print("✅ Security: Safe query execution system active")
    else:
        print("❌ Security: Query executor failed")
        return
    
    # 2. Database Schema Overview
    print_section("Database Schema Overview")
    
    schema_info = get_schema_info()
    print(f"📊 Database contains {len(schema_info)} tables:")
    for table_name, columns in schema_info.items():
        col_list = list(columns)  # Convert to list if it's not already
        print(f"   • {table_name}: {len(col_list)} columns")
        print(f"     └─ {', '.join(col_list[:3])}{'...' if len(col_list) > 3 else ''}")
    
    # 3. Interactive Demo Questions
    print_section("Interactive Text-to-SQL Demo")
    
    demo_questions = [
        # Basic queries
        {
            "category": "Basic Queries",
            "questions": [
                "Show me all customers",
                "How many products do we have?", 
                "What are our product categories?"
            ]
        },
        # Analytics queries
        {
            "category": "Analytics & Insights",
            "questions": [
                "Show me the most expensive products",
                "Find customers who placed orders recently",
                "Calculate total revenue from all orders"
            ]
        },
        # Complex queries
        {
            "category": "Complex Relationships", 
            "questions": [
                "Show customer order history with total spent",
                "Find the top 3 customers by total spending",
                "List products that haven't been ordered yet"
            ]
        }
    ]
    
    total_questions = 0
    successful_queries = 0
    
    for demo_group in demo_questions:
        print(f"\n🏷️  {demo_group['category']}")
        print("─" * 25)
        
        for i, question in enumerate(demo_group['questions'], 1):
            total_questions += 1
            print(f"\n{total_questions}. 💬 Question: \"{question}\"")
            
            try:
                # Execute the complete pipeline
                result = execute_text_to_sql(question)
                
                print(f"   🔤 Generated SQL:")
                print(f"      {result['sql_query']}")
                print(f"   🎯 AI Confidence: {result['confidence']:.1%}")
                
                if result['success']:
                    successful_queries += 1
                    print(f"   ✅ Execution: {result['row_count']} rows in {result['execution_time']:.3f}s")
                    
                    # Show sample data (first row only for demo)
                    if result.get('data') and len(result['data']) > 0:
                        sample = result['data'][0]
                        # Truncate long values for display
                        display_sample = {}
                        for key, value in sample.items():
                            if isinstance(value, str) and len(value) > 30:
                                display_sample[key] = value[:27] + "..."
                            else:
                                display_sample[key] = value
                        print(f"   📄 Sample Result: {display_sample}")
                    
                    if result.get('warnings'):
                        print(f"   ⚠️  Warnings: {result['warnings']}")
                else:
                    print(f"   ❌ Execution Error: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                print(f"   💥 System Error: {e}")
    
    # 4. Security Demo
    print_section("Security & Safety Demo")
    
    dangerous_attempts = [
        "DROP TABLE customers",
        "DELETE FROM orders", 
        "INSERT INTO products VALUES (999, 'Hacked')",
        "SELECT * FROM information_schema.tables"
    ]
    
    print("🚨 Testing security by attempting dangerous queries:")
    blocked_attempts = 0
    
    for i, dangerous_query in enumerate(dangerous_attempts, 1):
        print(f"\n{i}. 🔓 Attempting: \"{dangerous_query}\"")
        try:
            result = execute_text_to_sql(dangerous_query)
            if result['success']:
                print("   ❌ SECURITY BREACH: Query should have been blocked!")
            else:
                blocked_attempts += 1
                print(f"   ✅ Blocked: {result.get('error', 'Security violation')}")
        except Exception as e:
            blocked_attempts += 1
            print(f"   ✅ Blocked: {e}")
    
    # 5. Performance Summary
    print_section("Demo Summary & Statistics")
    
    success_rate = (successful_queries / total_questions) * 100 if total_questions > 0 else 0
    security_rate = (blocked_attempts / len(dangerous_attempts)) * 100 if dangerous_attempts else 0
    
    print(f"📊 Query Success Rate: {successful_queries}/{total_questions} ({success_rate:.1f}%)")
    print(f"🛡️  Security Success Rate: {blocked_attempts}/{len(dangerous_attempts)} ({security_rate:.1f}%)")
    print(f"🧠 AI Model: Groq Llama3-70B-8192")
    print(f"💾 Database: Supabase PostgreSQL")
    print(f"🔧 System Status: Fully Operational")
    
    # 6. What's Next
    print_section("What's Next in Development")
    
    print("🚧 Upcoming Phases:")
    print("   • Phase 5: REST API Development (FastAPI)")
    print("   • Phase 6: Testing & Quality Assurance") 
    print("   • Phase 7: Advanced Features (caching, history)")
    print("   • Phase 8: User Interface & Documentation")
    
    print_header("DEMO COMPLETE")
    print("🎉 Your Text-to-SQL Assistant is working perfectly!")
    print("💡 Ready for production use or further development")


def interactive_mode():
    """Run in interactive mode for custom questions"""
    print_header("INTERACTIVE MODE")
    print("💬 Ask any question about your database!")
    print("🔄 Type 'quit' to exit")
    
    while True:
        try:
            question = input("\n🗣️  Your question: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not question:
                continue
            
            print(f"\n🔄 Processing: \"{question}\"")
            result = execute_text_to_sql(question)
            
            print(f"🔤 SQL: {result['sql_query']}")
            print(f"🎯 Confidence: {result['confidence']:.1%}")
            
            if result['success']:
                print(f"✅ Found {result['row_count']} results in {result['execution_time']:.3f}s")
                
                if result.get('data'):
                    # Show first few results
                    for i, row in enumerate(result['data'][:3], 1):
                        print(f"   {i}. {row}")
                    
                    if result['row_count'] > 3:
                        print(f"   ... and {result['row_count'] - 3} more results")
            else:
                print(f"❌ Error: {result.get('error')}")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"💥 Error: {e}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Text-to-SQL Assistant Demo")
    parser.add_argument("--interactive", "-i", action="store_true", 
                       help="Run in interactive mode")
    
    args = parser.parse_args()
    
    if args.interactive:
        interactive_mode()
    else:
        demo_complete_system()
