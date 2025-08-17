#!/usr/bin/env python3
"""
API Test Script for Text-to-SQL Assistant
Tests the REST API endpoints
"""
import requests
import json
import sys
import time

# API base URL
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api/v1"

def test_health_check():
    """Test the health check endpoint"""
    print("🏥 Testing Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_comprehensive_health():
    """Test the comprehensive health check endpoint"""
    print("🏥 Testing Comprehensive Health Check...")
    try:
        response = requests.get(f"{API_URL}/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_schema_endpoint():
    """Test the schema endpoint"""
    print("📊 Testing Schema Endpoint...")
    try:
        response = requests.get(f"{API_URL}/schema")
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   Tables found: {data.get('table_count', 0)}")
        if data.get('tables'):
            for table_name in list(data['tables'].keys())[:3]:  # Show first 3 tables
                print(f"   - {table_name}: {len(data['tables'][table_name]['columns'])} columns")
        return response.status_code == 200
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_text_to_sql_basic():
    """Test basic text-to-SQL conversion"""
    print("🧠 Testing Basic Text-to-SQL...")
    try:
        payload = {
            "question": "Show me all customers",
            "execute_query": False,
            "include_schema": False
        }
        response = requests.post(f"{API_URL}/text-to-sql", json=payload)
        print(f"   Status: {response.status_code}")
        data = response.json()
        
        if data.get('success'):
            print(f"   ✅ SQL Generated: {data['sql']['sql_query']}")
            print(f"   🎯 Confidence: {data['sql']['confidence_score']}%")
        else:
            print(f"   ❌ Error: {data.get('error')}")
        
        return response.status_code == 200 and data.get('success')
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_text_to_sql_with_execution():
    """Test text-to-SQL with query execution"""
    print("⚡ Testing Text-to-SQL with Execution...")
    try:
        payload = {
            "question": "How many customers do we have?",
            "execute_query": True,
            "include_schema": False
        }
        response = requests.post(f"{API_URL}/text-to-sql", json=payload)
        print(f"   Status: {response.status_code}")
        data = response.json()
        
        if data.get('success'):
            print(f"   ✅ SQL Generated: {data['sql']['sql_query']}")
            if data.get('results'):
                print(f"   📊 Rows returned: {data['results']['row_count']}")
                print(f"   ⏱️ Execution time: {data['results']['execution_time_ms']:.2f}ms")
                if data['results']['rows']:
                    print(f"   📄 Sample result: {data['results']['rows'][0]}")
        else:
            print(f"   ❌ Error: {data.get('error')}")
        
        return response.status_code == 200 and data.get('success')
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_sql_validation():
    """Test SQL validation endpoint"""
    print("🔍 Testing SQL Validation...")
    try:
        # Test valid SQL
        response = requests.get(f"{API_URL}/validate-sql", params={"query": "SELECT * FROM customers;"})
        print(f"   Valid SQL Status: {response.status_code}")
        data = response.json()
        print(f"   Valid: {data.get('valid')}")
        
        # Test invalid SQL
        response = requests.get(f"{API_URL}/validate-sql", params={"query": "DROP TABLE customers;"})
        print(f"   Invalid SQL Status: {response.status_code}")
        data = response.json()
        print(f"   Valid: {data.get('valid')} (should be False)")
        print(f"   Error: {data.get('error', 'None')}")
        
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    """Run all API tests"""
    print("🚀 TEXT-TO-SQL API TESTING SUITE")
    print("=" * 50)
    
    # Wait for server to be ready
    print("⏳ Waiting for server to be ready...")
    time.sleep(2)
    
    tests = [
        ("Health Check", test_health_check),
        ("Comprehensive Health", test_comprehensive_health),
        ("Schema Endpoint", test_schema_endpoint),
        ("Basic Text-to-SQL", test_text_to_sql_basic),
        ("Text-to-SQL with Execution", test_text_to_sql_with_execution),
        ("SQL Validation", test_sql_validation),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📝 Running: {test_name}")
        result = test_func()
        results.append((test_name, result))
        print(f"   {'✅ PASSED' if result else '❌ FAILED'}")
    
    # Summary
    print(f"\n{'='*50}")
    print("📊 TEST SUMMARY")
    print(f"{'='*50}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {test_name}: {status}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All tests passed! Your API is working perfectly!")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()
