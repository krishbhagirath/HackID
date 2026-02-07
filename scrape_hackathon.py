"""
Scrape all projects from a hackathon's Devpost gallery.
This script automatically finds all project URLs and scrapes each one.
"""

from scraper import DevpostScraper, save_to_json
import os
import time
import argparse


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
    
    # Step 1: Get hackathon schedule
    print("\n[Step 1] Fetching hackathon schedule...")
    schedule = scraper.scrape_hackathon_schedule(hackathon_url)
    
    if schedule:
        print(f"✓ Found {len(schedule)} schedule event(s)")
        for event in schedule:
            print(f"  • {event['period']}: {event['start_time']} → {event['end_time']}")
        print()
    else:
        print("⚠️  No schedule found (continuing anyway)\n")
    
    # Step 2: Get all project URLs from the gallery
    print("[Step 2] Fetching project URLs from gallery...")
    project_urls = scraper.scrape_hackathon_gallery(hackathon_url, max_projects=max_projects)
    
    if not project_urls:
        print("❌ No projects found or error occurred")
        return
    
    print(f"✓ Found {len(project_urls)} project(s) to scrape\n")
    
    # Step 3: Scrape each project
    print("[Step 3] Scraping individual projects...\n")
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
            
            # Append schedule information to project
            if schedule:
                # Find the "Submissions" period for start/end times
                submissions_period = next((s for s in schedule if s['period'] == 'Submissions'), None)
                if submissions_period:
                    project_data['start_time'] = submissions_period['start_time']
                    project_data['end_time'] = submissions_period['end_time']
                else:
                    # If no Submissions period, use first schedule event
                    project_data['start_time'] = schedule[0]['start_time'] if schedule else ''
                    project_data['end_time'] = schedule[0]['end_time'] if schedule else ''
            else:
                project_data['start_time'] = ''
                project_data['end_time'] = ''
            
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
    
    # Step 4: Save all data together
    if all_projects:
        # Combine schedule and projects into final output
        final_output = {
            'hackathon_url': hackathon_url,
            'schedule': schedule,
            'projects': all_projects
        }
        save_to_json(final_output, 'output/all_hackathon_projects.json')
        
        print("="*80)
        print(" SUMMARY")
        print("="*80)
        print(f"✓ Schedule events: {len(schedule)}")
        print(f"✓ Successfully scraped: {successful} project(s)")
        if failed > 0:
            print(f"❌ Failed: {failed} project(s)")
        print(f"💾 All data saved to: output/all_hackathon_projects.json")
        print("="*80)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Scrape all projects from a hackathon\'s Devpost gallery.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Scrape DeltaHacks 12 (first 10 projects, 2.5s delay)
  python scrape_hackathon.py https://deltahacks-12.devpost.com/
  
  # Scrape up to 50 projects with 3 second delays
  python scrape_hackathon.py https://some-hackathon.devpost.com/ --max-projects 50 --delay 3
  
  # Scrape all projects (no limit) with 1 second delays
  python scrape_hackathon.py https://another-hackathon.devpost.com/ --max-projects 0 --delay 1
        '''
    )
    
    parser.add_argument(
        'url',
        help='URL to the hackathon page (e.g., https://deltahacks-12.devpost.com/)'
    )
    parser.add_argument(
        '--max-projects',
        type=int,
        default=10,
        help='Maximum number of projects to scrape (default: 10, use 0 for unlimited)'
    )
    parser.add_argument(
        '--delay',
        type=float,
        default=2.5,
        help='Delay in seconds between scraping projects (default: 2.5)'
    )
    
    args = parser.parse_args()
    
    # Convert 0 to None for unlimited projects
    max_projects = args.max_projects if args.max_projects > 0 else None
    
    scrape_entire_hackathon(
        hackathon_url=args.url,
        max_projects=max_projects,
        delay_seconds=args.delay
    )