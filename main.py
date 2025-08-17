"""
Text-to-SQL Assistant
A natural language AI assistant that converts user questions into SQL queries.
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.utils.logger import setup_logging, get_logger

# Initialize logging
setup_logging()
logger = get_logger(__name__)


def main():
    """Main application entry point"""
    logger.info("Starting Text-to-SQL Assistant...")
    
    try:
        # Import here to ensure logging is set up first
        from src.api.app import create_app
        import uvicorn
        from config.settings import get_settings
        
        settings = get_settings()
        
        # Create FastAPI app
        app = create_app()
        
        logger.info(f"Starting server on {settings.api_host}:{settings.api_port}")
        
        # Run the application
        uvicorn.run(
            app,
            host=settings.api_host,
            port=settings.api_port,
            log_config=None,  # Use our custom logging
            access_log=False  # Disable uvicorn access log
        )
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
