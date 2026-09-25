import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# We'll use a local SQLite database for maximum portability and simplicity
DATABASE_URL = "sqlite:///./sih_artisan.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to get the database session in route handlers
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
