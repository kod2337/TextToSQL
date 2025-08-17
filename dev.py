#!/usr/bin/env python3
"""
Development utilities for Text-to-SQL Assistant
Quick access to tests, d        print(f"\n🔧 Choose an option:")
        
        for key, option in options.items():
            print(f"  {key}. {option['name']}")
        
        print("  0. Exit")
        
        choice = input("\n🎯 Enter your choice (0-12): ").strip()d debug tools
"""

import sys
import subprocess
import os
from pathlib import Path

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.absolute()

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🚀 {description}")
    print(f"📍 Running: {command}")
    print("-" * 50)
    
    try:
        # Change to project root
        os.chdir(PROJECT_ROOT)
        
        # Run the command
        result = subprocess.run(command, shell=True, check=True)
        print(f"✅ {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with exit code {e.returncode}")
        return False
    except Exception as e:
        print(f"❌ Error running {description}: {e}")
        return False

def main():
    """Main menu for development utilities"""
    
    print("=" * 60)
    print("🎯 TEXT-TO-SQL ASSISTANT - DEVELOPMENT UTILITIES")
    print("=" * 60)
    
    options = {
        "1": {
            "name": "Run Complete System Demo",
            "command": f"{sys.executable} demo/demo_complete_system.py",
            "description": "Interactive demonstration of all system features"
        },
        "2": {
            "name": "Run All Tests",
            "command": f"{sys.executable} -m pytest tests/ -v",
            "description": "Execute all unit and integration tests"
        },
        "3": {
            "name": "Run Database Tests",
            "command": f"{sys.executable} tests/test_db.py",
            "description": "Test database connectivity and queries"
        },
        "4": {
            "name": "Run Groq API Tests",
            "command": f"{sys.executable} tests/test_groq.py",
            "description": "Test Groq AI integration"
        },
        "5": {
            "name": "Run End-to-End Tests",
            "command": f"{sys.executable} tests/test_end_to_end.py",
            "description": "Test complete pipeline functionality"
        },
        "6": {
            "name": "Debug Question Extraction",
            "command": f"{sys.executable} debug/debug_extraction.py",
            "description": "Debug question extraction from prompts"
        },
        "7": {
            "name": "Debug Prompt Generation",
            "command": f"{sys.executable} debug/debug_prompt.py",
            "description": "Debug prompt formatting and generation"
        },
        "8": {
            "name": "Debug SQL Generation",
            "command": f"{sys.executable} debug/debug_sql.py",
            "description": "Debug SQL generation and validation"
        },
        "9": {
            "name": "Run Main Application",
            "command": f"{sys.executable} main.py",
            "description": "Start the main Text-to-SQL application"
        },
        "10": {
            "name": "Start API Server",
            "command": f"{sys.executable} server.py",
            "description": "Start the FastAPI REST API server"
        },
        "11": {
            "name": "Test API Endpoints",
            "command": f"{sys.executable} tests/test_api.py",
            "description": "Test all REST API endpoints"
        },
        "12": {
            "name": "Open Web Interface",
            "command": "start http://localhost:8000",
            "description": "Open the web interface in browser (start server first)"
        }
    }
    
    while True:
        print(f"\n📂 Current directory: {PROJECT_ROOT}")
        print("\n🔧 Choose an option:")
        
        for key, option in options.items():
            print(f"  {key}. {option['name']}")
        
        print("  0. Exit")
        
        choice = input("\n🎯 Enter your choice (0-9): ").strip()
        
        if choice == "0":
            print("\n👋 Goodbye!")
            break
        elif choice in options:
            option = options[choice]
            success = run_command(option["command"], option["description"])
            
            if not success:
                print(f"\n⚠️  {option['name']} encountered issues.")
                print("Check the output above for details.")
            
            input("\n⏯️  Press Enter to continue...")
        else:
            print("\n❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
