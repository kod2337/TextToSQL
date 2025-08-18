#!/usr/bin/env python3
"""
FastAPI server for Text-to-SQL Assistant
Run this script to start the API server
"""
import uvicorn
import sys
import os
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from src.api.app import create_app
from src.utils.logger import get_logger

logger = get_logger(__name__)

def main():
    """Main function to start the server"""
    try:
        logger.info("Starting Text-to-SQL Assistant API server...")
        
        # Create the FastAPI app
        app = create_app()
        
        # Run the server
        uvicorn.run(
            "src.api.app:create_app",
            factory=True,
            host="127.0.0.1",
            port=8001,
            reload=True,
            log_level="info"
        )
        
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
