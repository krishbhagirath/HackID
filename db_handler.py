
import os
import json
import glob
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, String, DateTime, text, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in .env file")

# Setup SQLAlchemy
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- Database Models ---

class Submission(Base):
    __tablename__ = 'submissions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    org_id = Column(String, nullable=False)
    event_id = Column(String, nullable=False)
    source = Column(String, nullable=False)
    source_url = Column(String, nullable=False, unique=True)
    title = Column(String)
    tagline = Column(String)
    github_repo = Column(String)
    hackathon = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    raw_data = relationship("RawSubmission", back_populates="submission", uselist=False)
    text_sections = relationship("SubmissionText", back_populates="submission", cascade="all, delete-orphan")

class RawSubmission(Base):
    __tablename__ = 'raw_submissions'
    
    submission_id = Column(UUID(as_uuid=True), ForeignKey('submissions.id'), primary_key=True)
    raw_json = Column(JSONB, nullable=False)
    scraped_at = Column(DateTime(timezone=True), server_default=func.now())
    
    submission = relationship("Submission", back_populates="raw_data")

class SubmissionText(Base):
    __tablename__ = 'submission_text'
    
    submission_id = Column(UUID(as_uuid=True), ForeignKey('submissions.id'), primary_key=True)
    section_key = Column(String, primary_key=True)
    section_text = Column(String, nullable=False)
    
    submission = relationship("Submission", back_populates="text_sections")

# --- Logic ---

DEFAULT_ORG_ID = "default-org"
DEFAULT_EVENT_ID = "hackathon-event"

def save_project_to_db(data, org_id=DEFAULT_ORG_ID, event_id=DEFAULT_EVENT_ID):
    """
    Save a single project dictionary to the database using SQLAlchemy.
    Updates existing records if source_url matches.
    """
    session = SessionLocal()
    try:
        source_url = data['url']
        
        # 1. Check for existing submission
        submission = session.query(Submission).filter(Submission.source_url == source_url).first()
        
        if submission:
            # Update existing
            submission.title = data.get('title')
            submission.tagline = data.get('tagline')
            submission.github_repo = data.get('github_repo')
            submission.hackathon = data.get('hackathon')
            # updated_at will handle itself via onupdate or we can force it
            # submission.updated_at = func.now() 
        else:
            # Create new
            submission = Submission(
                org_id=org_id,
                event_id=event_id,
                source='devpost',
                source_url=source_url,
                title=data.get('title'),
                tagline=data.get('tagline'),
                github_repo=data.get('github_repo'),
                hackathon=data.get('hackathon')
            )
            session.add(submission)
            session.flush() # Flush to generate the ID for new records

        # 2. Update/Insert Raw Data
        if submission.raw_data:
            submission.raw_data.raw_json = data
            submission.raw_data.scraped_at = func.now()
        else:
            raw_node = RawSubmission(
                submission_id=submission.id, 
                raw_json=data
            )
            session.add(raw_node)
            
        # 3. Update Text Sections
        # Easiest way with ORM: Clear list and re-add. 
        # cascade="all, delete-orphan" on the relationship handles the DELETE.
        submission.text_sections = [] 
        
        story = data.get('story', {})
        for section_key, section_text in story.items():
            if section_key and section_text:
                text_node = SubmissionText(
                    section_key=section_key,
                    section_text=section_text
                )
                submission.text_sections.append(text_node)

        session.commit()
        return submission.id, True

    except Exception as e:
        session.rollback()
        print(f"[ERROR] Saving project '{data.get('title', 'Unknown')}': {e}")
        return None, False
    finally:
        session.close()

def process_output_folder(folder_path="output"):
    """
    Read all JSON files from the output folder and save them to the database.
    Preferentially uses 'all_hackathon_projects.json' if it exists.
    """
    # Check for the main summary file first
    summary_file = os.path.join(folder_path, "all_hackathon_projects.json")
    
    if os.path.exists(summary_file):
        print(f"Processing summary file: {summary_file}")
        try:
            with open(summary_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            projects = data.get('projects', [])
            event_id = data.get('hackathon_url', DEFAULT_EVENT_ID)
            
            print(f"Found {len(projects)} projects to import.")
            
            success_count = 0
            for project in projects:
                _, success = save_project_to_db(project, event_id=event_id)
                if success:
                    success_count += 1
                    print(f"[OK] Saved: {project.get('title')}")
            
            print(f"\nImport complete. Successfully saved {success_count}/{len(projects)} projects.")
            return
            
        except Exception as e:
            print(f"Error reading summary file: {e}")
            print("Falling back to individual files...")

    # Fallback to individual files
    json_files = glob.glob(os.path.join(folder_path, "*.json"))
    project_files = [f for f in json_files if "all_hackathon_projects.json" not in f]
    
    print(f"Processing {len(project_files)} individual project files...")
    
    success_count = 0
    for file_path in project_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            if 'url' in data and 'title' in data:
                _, success = save_project_to_db(data)
                if success:
                    success_count += 1
                    print(f"[OK] Saved: {data.get('title')} (from {os.path.basename(file_path)})")
        except Exception as e:
            print(f"Skipping file {file_path}: {e}")
            
    print(f"\nImport complete. Successfully saved {success_count} projects.")

if __name__ == "__main__":
    process_output_folder()
