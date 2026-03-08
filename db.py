import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# We'll use environment variables for security
DB_URL = os.getenv("DATABASE_URL")

if not DB_URL:
    # Use SQLite for local development by default if no DATABASE_URL is set
    DB_URL = "sqlite:///./cricpredict.db"
    print(f"Warning: DATABASE_URL not found. Using local SQLite: {DB_URL}")

engine = create_engine(DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
