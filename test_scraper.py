"""
Test script to demonstrate scraping DeltaHacks 12 projects.
"""

from scraper import DevpostScraper, save_to_json
import os


def main():
    """Test the scraper on multiple DeltaHacks 12 projects."""
    
    # Create output directory if it doesn't exist
    os.makedirs('output', exist_ok=True)
    
    # Initialize scraper
    scraper = DevpostScraper()
    
    # List of DeltaHacks 12 projects to test
    test_projects = [
        'https://devpost.com/software/deltawash',
        'https://devpost.com/software/fleetguard-180jd9?_gl=1*18hckc4*_gcl_au*MTQyNjg4MjA3NS4xNzY4MzIwMzcy*_ga*MTg4MDI2ODg1LjE3NjgzMjAzNzI.*_ga_0YHJK3Y10M*czE3NzA0ODE5MzUkbzIkZzEkdDE3NzA0ODI4MjckajQ3JGwwJGgw',
        # Add more project URLs here as needed
    ]
    
    print("="*70)
    print(" DEVPOST SCRAPER TEST - DeltaHacks 12")
    print("="*70)
    
    all_projects = []
    
    for i, project_url in enumerate(test_projects, 1):
        print(f"\n[{i}/{len(test_projects)}] Scraping: {project_url}")
        print("-"*70)
        
        project_data = scraper.scrape_project(project_url)
        
        if 'error' in project_data:
            print(f"❌ ERROR: {project_data['error']}")
            continue
        
        # Display key information
        print(f"✓ Title: {project_data['title']}")
        print(f"✓ Tagline: {project_data['tagline']}")
        print(f"✓ Hackathon: {project_data['hackathon']}")
        print(f"✓ Tech Stack ({len(project_data['built_with'])}): {', '.join(project_data['built_with'][:5])}")
        if len(project_data['built_with']) > 5:
            print(f"  ... and {len(project_data['built_with']) - 5} more")
        print(f"✓ GitHub Repo: {project_data['github_repo'] or 'Not found'}")
        print(f"✓ Team Members ({len(project_data['team_members'])}): {', '.join([m['name'] for m in project_data['team_members']])}")
        print(f"✓ External Links: {len(project_data['links'])}")
        print(f"✓ Story Sections: {', '.join(project_data['story'].keys())}")
        
        if project_data['prizes']:
            print(f"🏆 Prizes: {', '.join(project_data['prizes'])}")
        
        # Show a preview of one story section
        if project_data['story']:
            first_section = list(project_data['story'].keys())[0]
            preview = project_data['story'][first_section][:150]
            print(f"\n📝 Preview of '{first_section}':")
            print(f"   {preview}...")
        
        all_projects.append(project_data)
        
        # Save individual project
        filename = f"output/{project_data['title'].replace(' ', '_').lower()}.json"
        save_to_json(project_data, filename)
        print(f"\n💾 Saved to: {filename}")
    
    # Save all projects together
    if all_projects:
        save_to_json(all_projects, 'output/all_scraped_projects.json')
        print(f"\n{'='*70}")
        print(f"✓ Successfully scraped {len(all_projects)} project(s)")
        print(f"✓ All data saved to: output/all_scraped_projects.json")
        print(f"{'='*70}\n")


if __name__ == '__main__':
    main()
