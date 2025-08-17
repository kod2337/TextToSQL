#!/usr/bin/env python3
"""
Direct test of Groq API to debug the issue
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from groq import Groq
from config.settings import get_settings

def test_groq_direct():
    """Test Groq API directly"""
    settings = get_settings()
    
    if not settings.groq_api_key:
        print("❌ No Groq API key found")
        return
    
    try:
        client = Groq(api_key=settings.groq_api_key)
        
        prompt = """Database Schema:
Tables:
1. customers: id, first_name, last_name, email, phone, created_at
2. products: id, name, description, price, category, stock_quantity  
3. orders: id, customer_id, order_date, total_amount
4. order_items: id, order_id, product_id, quantity, price

Question: Find orders from last month with customer details

SQL Query:"""

        print("🚀 Testing Groq API directly...")
        print(f"Model: {settings.groq_model}")
        print(f"Prompt: {prompt}")
        print("-" * 50)
        
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert SQL query generator. Generate ONLY the SQL query, no explanations."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            model=settings.groq_model,
            temperature=0.1,
            max_tokens=200,
        )
        
        result = chat_completion.choices[0].message.content.strip()
        print(f"✅ Groq Response: {result}")
        
        # Test with a simpler question
        print("\n" + "="*50)
        print("Testing with simpler question...")
        
        simple_prompt = """Database: customers table with columns (id, first_name, last_name, email)
Question: Show all customers
SQL:"""
        
        chat_completion2 = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "Generate only SQL query, no explanations or formatting."
                },
                {
                    "role": "user", 
                    "content": simple_prompt
                }
            ],
            model=settings.groq_model,
            temperature=0.1,
            max_tokens=100,
        )
        
        result2 = chat_completion2.choices[0].message.content.strip()
        print(f"✅ Simple Query Response: {result2}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_groq_direct()
