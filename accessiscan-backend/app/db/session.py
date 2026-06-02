"""
PERSISTENCE LAYER & DATABASE SESSION FACTORY
---------------------------------------------------------------------
Purpose:
    Manages the initialization of the SQLAlchemy database engine, maps 
    schemas, and handles operational transaction connections via SQLModel.

Architecture:
    1. Lazy Factory: Defers engine compilation to prevent startup conflicts 
       and ensure compatibility with test runners.
    2. Circular Dependency Resolution: Uses local imports for schema 
       registration to maintain system modularity.
    3. Session Isolation: Guarantees transactional integrity per 
       incoming request scope.
"""

from typing import Generator
from sqlmodel import SQLModel, Session, create_engine
from app.core.config import settings

# Global state for the engine factory
_engine = None

# --- 1. ENGINE FACTORY ---
# Purpose: Implement a Lazy Factory pattern. By deferring instantiation 
# until the first request, the system ensures stable connection binding.
def get_engine():
    """Instantiates the SQLAlchemy engine pool on first request."""
    global _engine
    if _engine is None:
        # SQLite requires specific arguments for multi-threaded access
        connect_args = {"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
        _engine = create_engine(
            settings.DATABASE_URL, 
            echo=settings.DEBUG, 
            connect_args=connect_args
        )
    return _engine

# --- 2. METADATA BOOTSTRAPPER ---
# Purpose: Register database tables. Performs local imports to resolve 
# circular dependency issues inherent in complex relational layouts.
def create_db_and_tables() -> None:
    """Applies relational table definitions to the database engine."""
    # Local imports prevent circular dependency during startup
    from app.models.user import User
    from app.models.inspection import Inspection
    from app.models.detection import Detection
    from app.models.report import Report
    from app.models.image import Image  
    
    engine = get_engine()
    SQLModel.metadata.create_all(engine)

# --- 3. SESSION GENERATOR ---
# Purpose: Provide a context-managed transactional boundary. Ensures 
# each request receives an isolated session that disposes upon completion.
def get_session() -> Generator[Session, None, None]:
    """Yields an isolated relational database transaction."""
    engine = get_engine()
    with Session(engine) as session:
        yield session

# Global instance for background worker tasks
engine = get_engine()