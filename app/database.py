import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

default_sqlite_url = "sqlite:///./students.db"
if os.getenv("VERCEL"):
    # Vercel serverless functions can only write to /tmp.
    # This keeps the demo deploy running, but data may reset between cold starts.
    default_sqlite_url = "sqlite:////tmp/students.db"

DATABASE_URL = os.getenv("DATABASE_URL", default_sqlite_url)

# Handle standard postgres:// URLs to be compatible with SQLAlchemy (expects postgresql://)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# check_same_thread=False is required only for SQLite.
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

# Create the engine
engine = create_engine(
    DATABASE_URL, connect_args=connect_args
)

# Create a SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a Base class for models
Base = declarative_base()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
