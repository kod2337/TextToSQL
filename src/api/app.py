from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.settings import get_settings
from src.utils.logger import get_logger
from src.api.routes import get_router
from src.api.web_routes import get_web_router
from src.database.connection import test_connection

logger = get_logger(__name__)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    settings = get_settings()
    
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="A natural language AI assistant that converts user questions into SQL queries",
        debug=settings.debug
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include web interface routes (must be included BEFORE the root route)
    web_router = get_web_router()
    app.include_router(web_router, tags=["Web Interface"])
    
    # Include API routes
    api_router = get_router()
    app.include_router(api_router, prefix="/api/v1", tags=["Text-to-SQL"])
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Simple health check endpoint"""
        db_status = "unknown"
        try:
            conn_info = test_connection()
            db_status = "connected" if conn_info.get("success") else "disconnected"
        except Exception:
            db_status = "disconnected"
            
        return {
            "status": "healthy" if db_status == "connected" else "degraded",
            "app_name": settings.app_name,
            "version": settings.app_version,
            "database_status": db_status
        }
    
    logger.info("FastAPI application created successfully")
    return app


# Create the app instance for direct uvicorn access
app = create_app()
