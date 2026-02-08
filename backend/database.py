import os
import uuid
from datetime import datetime
from sqlalchemy import create_engine, Column, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

class Hackathon(Base):
    __tablename__ = "hackathons"

    hackathon_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(String, nullable=False)
    name = Column(String, nullable=False)
    devpost_url = Column(String, nullable=False, unique=True)
    start_time = Column(DateTime(timezone=True))
    end_time = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    projects = relationship("Project", back_populates="hackathon")

class Project(Base):
    __tablename__ = "projects"

    project_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    hackathon_id = Column(UUID(as_uuid=True), ForeignKey("hackathons.hackathon_id"), nullable=False)
    source_url = Column(String, nullable=False)
    title = Column(String, nullable=False)
    github_repo_link = Column(String)
    data = Column(JSONB)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    hackathon = relationship("Hackathon", back_populates="projects")

def get_db():
    """Dependency for getting a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize the database (create tables)."""
    Base.metadata.create_all(bind=engine)
    print("Database tables created.")

if __name__ == "__main__":
    # Quick connectivity test
    try:
        with engine.connect() as connection:
            print("Successfully connected to Supabase!")
    except Exception as e:
        print(f"Connection failed: {e}")
