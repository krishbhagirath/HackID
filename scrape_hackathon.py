"""
Scrape all projects from a hackathon's Devpost gallery.
This script automatically finds all project URLs and scrapes each one.
"""

from scraper import DevpostScraper, save_to_json
import os
import time


def scrape_entire_hackathon(hackathon_url: str, max_projects: int = 10, delay_seconds: float = 2.5):
    """
    Scrape all projects from a hackathon.
    
    Args:
        hackathon_url: URL to the hackathon page (e.g., https://deltahacks-12.devpost.com/)
        max_projects: Maximum number of projects to scrape (for testing)
        delay_seconds: Delay between scraping projects to avoid rate limiting
    """
    # Create output directory
    os.makedirs('output', exist_ok=True)
    
    # Initialize scraper
    scraper = DevpostScraper()
    
    print("="*80)
    print(" HACKATHON BATCH SCRAPER")
    print("="*80)
    print(f"Hackathon URL: {hackathon_url}")
    print(f"Max projects: {max_projects}")
    print(f"Delay between projects: {delay_seconds}s")
    print("="*80)
    
    # Step 1: Get all project URLs from the gallery
    print("\n[Step 1] Fetching project URLs from gallery...")
    project_urls = scraper.scrape_hackathon_gallery(hackathon_url, max_projects=max_projects)
    
    if not project_urls:
        print("❌ No projects found or error occurred")
        return
    
    print(f"✓ Found {len(project_urls)} project(s) to scrape\n")
    
    # Step 2: Scrape each project
    print("[Step 2] Scraping individual projects...\n")
    all_projects = []
    successful = 0
    failed = 0
    
    for i, project_url in enumerate(project_urls, 1):
        print(f"[{i}/{len(project_urls)}] {project_url}")
        print("-"*80)
        
        try:
            project_data = scraper.scrape_project(project_url)
            
            if 'error' in project_data:
                print(f"❌ ERROR: {project_data['error']}\n")
                failed += 1
                continue
            
            # Display summary
            print(f"✓ {project_data['title']}")
            print(f"  Tech: {', '.join(project_data['built_with'][:5])}")
            if len(project_data['built_with']) > 5:
                print(f"       (+{len(project_data['built_with']) - 5} more)")
            print(f"  Team: {len(project_data['team_members'])} member(s)")
            print(f"  GitHub: {project_data['github_repo'] or 'Not found'}")
            
            all_projects.append(project_data)
            successful += 1
            
            # Save individual project
            safe_filename = project_data['title'].replace(' ', '_').replace('/', '_').lower()
            filename = f"output/{safe_filename}.json"
            save_to_json(project_data, filename)
            print(f"  💾 Saved to: {filename}")
            
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            failed += 1
        
        # Rate limiting: wait between projects (except for last one)
        if i < len(project_urls):
            print(f"⏳ Waiting {delay_seconds}s before next project...\n")
            time.sleep(delay_seconds)
        else:
            print()  # Just add newline for last project
    
    # Step 3: Save all projects together
    if all_projects:
        save_to_json(all_projects, 'output/all_hackathon_projects.json')
        
        print("="*80)
        print(" SUMMARY")
        print("="*80)
        print(f"✓ Successfully scraped: {successful} project(s)")
        if failed > 0:
            print(f"❌ Failed: {failed} project(s)")
        print(f"💾 All data saved to: output/all_hackathon_projects.json")
        print("="*80)


if __name__ == '__main__':
    # Example: Scrape DeltaHacks 12
    hackathon_url = 'https://deltahacks-12.devpost.com/'
    
    # Scrape first 10 projects with 2.5 second delays
    scrape_entire_hackathon(
        hackathon_url=hackathon_url,
        max_projects=10,
        delay_seconds=2.5
    )
