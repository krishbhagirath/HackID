"""
Batch validation test for Mac-A-Thon 2025.
Validates 4 projects directly from the gallery.
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from pipeline import ValidationPipeline

# Load environment
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

def main():
    # Initialize pipeline
    pipeline = ValidationPipeline(
        google_api_key=os.getenv('GOOGLE_API_KEY'),
        github_token=os.getenv('GITHUB_TOKEN')
    )

    hackathon_url = "https://mac-a-thon-2025.devpost.com"
    
    print(f"🚀 Starting validation for Mac-A-Thon 2025...")
    
    # Run batch validation
    results = pipeline.validate_hackathon(
        hackathon_url=hackathon_url,
        max_projects=4,
        save_artifacts=False  # No files, console only as requested
    )

    # Final summary display
    print("\n" + "="*70)
    print("🏆 MAC-A-THON 2025 RESULTS")
    print("="*70)
    
    for i, res in enumerate(results, 1):
        status_color = "✅" if res.get('final_status') == "VERIFIED" else "🚩" if res.get('final_status') == "FLAGGED" else "❌"
        print(f"{i}. {status_color} {res.get('project_title')}")
        print(f"   Reasoning: {res.get('reasoning')}")
        print("-" * 30)

if __name__ == "__main__":
    main()
