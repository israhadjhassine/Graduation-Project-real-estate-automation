from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# The DATABASE_URL is fetched from the environment (defined in docker-compose or .env)
# Default is provided for local development if environment variable is missing
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://real_estate_user:secure_password_here@postgres:5432/real_estate_dev")

# Create the SQLAlchemy engine
# "engine" is the starting point for any SQLAlchemy application.
# It maintains a pool of connections to the database.
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Create a sessionmaker
# A Session is used to interact with the database (querying, adding, deleting).
# autocommit=False: We manually control when to "commit" changes to the DB.
# autoflush=False: Prevents sending changes to the DB until we are ready.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for our models
# All our database tables (models) will inherit from this class.
Base = declarative_base()

# Dependency for FastAPI routes
def get_db():
    """
    Creates a new database session for each request and closes it after the request is finished.
    This ensures that database connections are not leaked.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
