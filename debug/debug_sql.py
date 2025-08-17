#!/usr/bin/env python3
"""Test script for debugging SQL generation"""

from src.llm.pipeline import get_text_to_sql_pipeline

def test_full_pipeline():
    pipeline = get_text_to_sql_pipeline()
    
    print("🧠 Text-to-SQL Pipeline Test Results:")
    print("=" * 50)
    
    results = pipeline.test_pipeline()
    
    for question, result in results.items():
        print(f"\nQ: {question}")
        print(f"SQL: {result['query']}")
        print(f"Confidence: {result['confidence']:.2f}")
        print(f"Success: {result['success']}")

if __name__ == "__main__":
    test_full_pipeline()
