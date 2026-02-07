
import os
import json
import glob
import psycopg2
from psycopg2.extras import Json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Define default IDs for organization and event since they are required by the schema
# In a real application, these would come from your application logic/context
DEFAULT_ORG_ID = "default-org"
DEFAULT_EVENT_ID = "hackathon-event"

def get_db_connection():
    """Establish a connection to the database."""
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL is not set in .env file")
    return psycopg2.connect(DATABASE_URL)

def init_db():
    """Initialize the database schema."""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        print("Initializing database schema...")
        
        # 0. Enable pgcrypto extension for gen_random_uuid()
        cur.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto";')
        
        # 1. Create submissions table (must be first as others reference it)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS public.submissions (
          id uuid NOT NULL DEFAULT gen_random_uuid(),
          org_id text NOT NULL,
          event_id text NOT NULL,
          source text NOT NULL,
          source_url text NOT NULL UNIQUE,
          title text,
          tagline text,
          github_repo text,
          hackathon text,
          created_at timestamp with time zone DEFAULT now(),
          updated_at timestamp with time zone DEFAULT now(),
          CONSTRAINT submissions_pkey PRIMARY KEY (id)
        );
        """)
        
        # 2. Create raw_submissions table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS public.raw_submissions (
          submission_id uuid NOT NULL,
          raw_json jsonb NOT NULL,
          scraped_at timestamp with time zone DEFAULT now(),
          CONSTRAINT raw_submissions_pkey PRIMARY KEY (submission_id),
          CONSTRAINT raw_submissions_submission_id_fkey FOREIGN KEY (submission_id) REFERENCES public.submissions(id)
        );
        """)
        
        # 3. Create submission_text table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS public.submission_text (
          submission_id uuid NOT NULL,
          section_key text NOT NULL,
          section_text text NOT NULL,
          CONSTRAINT submission_text_pkey PRIMARY KEY (submission_id, section_key),
          CONSTRAINT submission_text_submission_id_fkey FOREIGN KEY (submission_id) REFERENCES public.submissions(id)
        );
        """)
        
        # 4. Create analysis_results table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS public.analysis_results (
          id uuid NOT NULL DEFAULT gen_random_uuid(),
          org_id text NOT NULL,
          event_id text NOT NULL,
          submission_id_a uuid,
          submission_id_b uuid,
          method text NOT NULL,
          version text NOT NULL,
          score numeric NOT NULL,
          severity text,
          explanation text,
          created_at timestamp with time zone DEFAULT now(),
          CONSTRAINT analysis_results_pkey PRIMARY KEY (id),
          CONSTRAINT analysis_results_submission_id_a_fkey FOREIGN KEY (submission_id_a) REFERENCES public.submissions(id),
          CONSTRAINT analysis_results_submission_id_b_fkey FOREIGN KEY (submission_id_b) REFERENCES public.submissions(id)
        );
        """)
        
        conn.commit()
        print("✓ Database schema initialized successfully.")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error initializing database: {e}")
        raise e
    finally:
        cur.close()
        conn.close()

def save_project_to_db(data, org_id=DEFAULT_ORG_ID, event_id=DEFAULT_EVENT_ID):
    """
    Save a single project dictionary to the database.
    Updates existing records if source_url matches.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # 1. Insert or Update into submissions
        # We check for existing URL to handle upserts
        cur.execute("SELECT id FROM submissions WHERE source_url = %s", (data['url'],))
        existing = cur.fetchone()
        
        submission_id = None
        
        if existing:
            submission_id = existing[0]
            # Update the existing record
            cur.execute("""
                UPDATE submissions 
                SET title = %s, tagline = %s, github_repo = %s, hackathon = %s, updated_at = NOW()
                WHERE id = %s
            """, (
                data.get('title'),
                data.get('tagline'),
                data.get('github_repo'),
                data.get('hackathon'),
                submission_id
            ))
        else:
            # Insert new record
            cur.execute("""
                INSERT INTO submissions (org_id, event_id, source, source_url, title, tagline, github_repo, hackathon)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                org_id,
                event_id,
                'devpost',
                data['url'],
                data.get('title'),
                data.get('tagline'),
                data.get('github_repo'),
                data.get('hackathon')
            ))
            submission_id = cur.fetchone()[0]
            
        # 2. Save raw JSON to raw_submissions
        # Upsert logic for raw_submissions
        cur.execute("""
            INSERT INTO raw_submissions (submission_id, raw_json)
            VALUES (%s, %s)
            ON CONFLICT (submission_id) 
            DO UPDATE SET raw_json = EXCLUDED.raw_json, scraped_at = NOW()
        """, (submission_id, Json(data)))
        
        # 3. Save text sections to submission_text
        # First, clear existing sections for this submission to avoid duplicates/stale data
        cur.execute("DELETE FROM submission_text WHERE submission_id = %s", (submission_id,))
        
        story = data.get('story', {})
        for section_key, section_text in story.items():
            if section_key and section_text:
                # Truncate section_key if needed (unlikely based on text type)
                cur.execute("""
                    INSERT INTO submission_text (submission_id, section_key, section_text)
                    VALUES (%s, %s, %s)
                """, (submission_id, section_key, section_text))
        
        conn.commit()
        return submission_id, True

    except Exception as e:
        conn.rollback()
        print(f"❌ Error saving project '{data.get('title', 'Unknown')}': {e}")
        return None, False
    finally:
        cur.close()
        conn.close()

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
            # Use the hackathon URL as event_id if present
            event_id = data.get('hackathon_url', DEFAULT_EVENT_ID)
            
            print(f"Found {len(projects)} projects to import.")
            
            success_count = 0
            for project in projects:
                _, success = save_project_to_db(project, event_id=event_id)
                if success:
                    success_count += 1
                    print(f"✓ Saved: {project.get('title')}")
            
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
                
            # Basic validation to ensure it's a project file
            if 'url' in data and 'title' in data:
                _, success = save_project_to_db(data)
                if success:
                    success_count += 1
                    print(f"✓ Saved: {data.get('title')} (from {os.path.basename(file_path)})")
        except Exception as e:
            print(f"Skipping file {file_path}: {e}")
            
    print(f"\nImport complete. Successfully saved {success_count} projects.")

if __name__ == "__main__":
    # When run directly, initialize DB and process the output folder
    init_db()
    process_output_folder()
