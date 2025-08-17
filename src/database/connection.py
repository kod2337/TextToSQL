"""
Database connection and session management
"""
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
from config.settings import get_settings
from src.utils.logger import get_logger
import asyncio
from typing import Generator

logger = get_logger(__name__)

# Create SQLAlchemy base class
Base = declarative_base()

# Global variables for database
engine = None
SessionLocal = None


def create_database_engine():
    """Create database engine"""
    global engine
    settings = get_settings()
    
    try:
        # Configure connection arguments for Supabase
        connect_args = {}
        if "supabase.co" in settings.database_url:
            connect_args = {
                "sslmode": "require",
                "connect_timeout": 30,
            }
        
        engine = create_engine(
            settings.database_url,
            poolclass=NullPool,  # Prevent connection pooling issues with serverless
            echo=settings.debug,  # Log SQL queries in debug mode
            future=True,  # Use SQLAlchemy 2.0 style
            connect_args=connect_args
        )
        logger.info("Database engine created successfully")
        return engine
    except Exception as e:
        logger.error(f"Failed to create database engine: {e}")
        raise


def create_session_factory():
    """Create session factory"""
    global SessionLocal
    if engine is None:
        create_database_engine()
    
    SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )
    logger.info("Session factory created successfully")
    return SessionLocal


def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get database session
    Use this in FastAPI endpoints
    """
    if SessionLocal is None:
        create_session_factory()
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_connection() -> bool:
    """Test database connection"""
    try:
        if engine is None:
            create_database_engine()
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            logger.info("Database connection test successful")
            return True
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False


def init_database():
    """Initialize database - create tables"""
    try:
        if engine is None:
            create_database_engine()
        
        # Import models to register them with Base
        from src.database.models import Customer, Product, Order, OrderItem
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


def get_schema_info() -> dict:
    """Get database schema information for LLM context"""
    try:
        if engine is None:
            create_database_engine()
        
        schema_info = {}
        
        with engine.connect() as conn:
            # Get table names
            tables_query = text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                AND table_type = 'BASE TABLE'
            """)
            tables = conn.execute(tables_query).fetchall()
            
            for table in tables:
                table_name = table[0]
                
                # Get column information
                columns_query = text("""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns 
                    WHERE table_name = :table_name
                    AND table_schema = 'public'
                    ORDER BY ordinal_position
                """)
                columns = conn.execute(columns_query, {"table_name": table_name}).fetchall()
                
                schema_info[table_name] = {
                    'columns': [
                        {
                            'name': col[0],
                            'type': col[1],
                            'nullable': col[2] == 'YES',
                            'default': col[3]
                        }
                        for col in columns
                    ]
                }
        
        logger.info(f"Retrieved schema info for {len(schema_info)} tables")
        return schema_info
        
    except Exception as e:
        logger.error(f"Failed to get schema info: {e}")
        return {}
