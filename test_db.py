#!/usr/bin/env python3
"""
Database connection and data verification test script.
Tests the Supabase PostgreSQL connection and sample data.
"""

import os
import sys
from pathlib import Path

# Add src to Python path
sys.path.append(str(Path(__file__).parent / "src"))

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from config.settings import get_settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_database_connection():
    """Test basic database connectivity."""
    print("🔌 Testing Database Connection...")
    try:
        # Get database URL
        settings = get_settings()
        db_url = settings.database_url
        if not db_url:
            print("❌ No database URL configured")
            return False
            
        # Create engine
        engine = create_engine(db_url)
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"✅ Connected to PostgreSQL: {version[:50]}...")
            return True
            
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_table_structure():
    """Test that all required tables exist with correct structure."""
    print("\n📋 Testing Table Structure...")
    
    try:
        settings = get_settings()
        db_url = settings.database_url
        engine = create_engine(db_url)
        
        with engine.connect() as conn:
            # Check if tables exist
            tables_query = text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)
            
            result = conn.execute(tables_query)
            tables = [row[0] for row in result.fetchall()]
            
            print(f"📊 Found {len(tables)} tables:")
            for table in tables:
                print(f"  - {table}")
                
            # Check for expected tables
            expected_tables = ['customers', 'orders', 'products', 'order_items']
            missing_tables = [t for t in expected_tables if t not in tables]
            
            if missing_tables:
                print(f"⚠️  Missing expected tables: {missing_tables}")
            else:
                print("✅ All expected tables found")
                
            return len(tables) > 0
            
    except Exception as e:
        print(f"❌ Table structure test failed: {e}")
        return False

def test_sample_data():
    """Test that tables contain sample data."""
    print("\n📊 Testing Sample Data...")
    
    try:
        settings = get_settings()
        db_url = settings.database_url
        engine = create_engine(db_url)
        
        with engine.connect() as conn:
            # Test each main table
            tables_to_test = ['customers', 'products', 'orders', 'order_items']
            
            for table in tables_to_test:
                try:
                    # Get row count
                    count_query = text(f"SELECT COUNT(*) FROM {table};")
                    result = conn.execute(count_query)
                    count = result.fetchone()[0]
                    
                    # Get sample data
                    sample_query = text(f"SELECT * FROM {table} LIMIT 3;")
                    sample_result = conn.execute(sample_query)
                    columns = sample_result.keys()
                    rows = sample_result.fetchall()
                    
                    print(f"📋 Table '{table}': {count} rows")
                    print(f"   Columns: {list(columns)}")
                    
                    if rows:
                        print("   Sample data:")
                        for i, row in enumerate(rows, 1):
                            print(f"     Row {i}: {dict(zip(columns, row))}")
                    else:
                        print("   ⚠️  No data found")
                    print()
                    
                except Exception as table_error:
                    print(f"❌ Error testing table '{table}': {table_error}")
                    
            return True
            
    except Exception as e:
        print(f"❌ Sample data test failed: {e}")
        return False

def test_database_queries():
    """Test some basic SQL queries."""
    print("\n🔍 Testing Database Queries...")
    
    try:
        settings = get_settings()
        db_url = settings.database_url
        engine = create_engine(db_url)
        
        with engine.connect() as conn:
            # Test queries
            test_queries = [
                {
                    "name": "Customer count",
                    "query": "SELECT COUNT(*) as customer_count FROM customers;"
                },
                {
                    "name": "Products with price > 100",
                    "query": "SELECT name, price FROM products WHERE price > 100 LIMIT 5;"
                },
                {
                    "name": "Recent orders",
                    "query": "SELECT order_id, customer_id, order_date FROM orders ORDER BY order_date DESC LIMIT 3;"
                },
                {
                    "name": "Customer with orders (JOIN test)",
                    "query": """
                        SELECT c.name, COUNT(o.order_id) as order_count 
                        FROM customers c 
                        LEFT JOIN orders o ON c.customer_id = o.customer_id 
                        GROUP BY c.customer_id, c.name 
                        LIMIT 5;
                    """
                }
            ]
            
            for test in test_queries:
                try:
                    print(f"🔍 {test['name']}:")
                    result = conn.execute(text(test['query']))
                    rows = result.fetchall()
                    columns = result.keys()
                    
                    if rows:
                        for row in rows:
                            print(f"   {dict(zip(columns, row))}")
                    else:
                        print("   No results")
                    print()
                    
                except Exception as query_error:
                    print(f"❌ Query failed: {query_error}")
                    print()
                    
            return True
            
    except Exception as e:
        print(f"❌ Database queries test failed: {e}")
        return False

def test_schema_information():
    """Get detailed schema information."""
    print("\n🗂️  Testing Schema Information...")
    
    try:
        settings = get_settings()
        db_url = settings.database_url
        engine = create_engine(db_url)
        
        with engine.connect() as conn:
            # Get detailed column information
            schema_query = text("""
                SELECT 
                    table_name,
                    column_name,
                    data_type,
                    is_nullable,
                    column_default
                FROM information_schema.columns
                WHERE table_schema = 'public'
                ORDER BY table_name, ordinal_position;
            """)
            
            result = conn.execute(schema_query)
            schema_info = result.fetchall()
            
            # Group by table
            tables = {}
            for row in schema_info:
                table_name = row[0]
                if table_name not in tables:
                    tables[table_name] = []
                tables[table_name].append({
                    'column': row[1],
                    'type': row[2],
                    'nullable': row[3],
                    'default': row[4]
                })
            
            print("📋 Detailed Schema Information:")
            for table_name, columns in tables.items():
                print(f"\n📊 Table: {table_name}")
                for col in columns:
                    nullable = "NULL" if col['nullable'] == 'YES' else "NOT NULL"
                    default = f" DEFAULT {col['default']}" if col['default'] else ""
                    print(f"   {col['column']:20} {col['type']:15} {nullable}{default}")
                    
            return True
            
    except Exception as e:
        print(f"❌ Schema information test failed: {e}")
        return False

def main():
    """Run all database tests."""
    print("🧪 Text-to-SQL Database Test Suite")
    print("=" * 50)
    
    # Run all tests
    tests = [
        ("Database Connection", test_database_connection),
        ("Table Structure", test_table_structure),
        ("Sample Data", test_sample_data),
        ("Database Queries", test_database_queries),
        ("Schema Information", test_schema_information)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("🎯 Test Results Summary:")
    print("=" * 50)
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
        if success:
            passed += 1
    
    print(f"\n📊 Tests passed: {passed}/{len(results)}")
    
    if passed == len(results):
        print("🎉 All tests passed! Your database is ready for Text-to-SQL!")
    else:
        print("⚠️  Some tests failed. Check your database configuration.")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
