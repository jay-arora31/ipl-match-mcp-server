import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base

# Database URL - using SQLite for simplicity
DATABASE_URL = "sqlite:///ipl_cricket.db"

# Create engine
engine = create_engine(DATABASE_URL, echo=False)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_db_session():
    """Get database session for direct use"""
    return SessionLocal()

def reset_database():
    """Drop and recreate all tables"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("Database reset successfully!")

def check_database():
    """Check if database exists and has tables"""
    if not os.path.exists("ipl_cricket.db"):
        return False
    
    # Try to query a table to see if it exists
    try:
        with engine.connect() as conn:
            result = conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = result.fetchall()
            return len(tables) > 0
    except:
        return False 