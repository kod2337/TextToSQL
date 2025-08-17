"""
Simple database connection test
"""
import os
import sys
sys.path.append('src')

from config.settings import get_settings

def test_db_connection():
    settings = get_settings()
    print(f"Testing connection to: {settings.database_url}")
    
    # Try basic psycopg2 connection
    try:
        import psycopg2
        
        # Parse the connection string
        db_url = settings.database_url
        if db_url.startswith("postgresql://"):
            db_url = db_url.replace("postgresql://", "")
        
        # Extract components
        user_pass, host_db = db_url.split("@")
        user, password = user_pass.split(":")
        host_port, database = host_db.split("/")
        host, port = host_port.split(":")
        
        print(f"Host: {host}")
        print(f"Port: {port}")
        print(f"Database: {database}")
        print(f"User: {user}")
        print(f"Password: {'*' * len(password)}")
        
        # Try connection
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        print("✅ Connection successful!")
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    test_db_connection()
