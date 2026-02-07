"""
Devpost Project Scraper
Extracts project information from Devpost submission pages.
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
import json
import re


class DevpostScraper:
    """Scraper for extracting data from Devpost project pages."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def scrape_hackathon_gallery(self, hackathon_url: str, max_projects: int = None) -> List[str]:
        """
        Scrape a hackathon's project gallery to get all project URLs.
        
        Args:
            hackathon_url: URL to the hackathon page (e.g., https://deltahacks-12.devpost.com/)
            max_projects: Optional limit on number of projects to return
            
        Returns:
            List of project URLs
        """
        try:
            # Ensure we're on the project gallery page
            if not hackathon_url.endswith('/project-gallery'):
                if hackathon_url.endswith('/'):
                    hackathon_url = hackathon_url + 'project-gallery'
                else:
                    hackathon_url = hackathon_url + '/project-gallery'
            
            print(f"Fetching project gallery: {hackathon_url}")
            response = self.session.get(hackathon_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all project links in the gallery
            project_urls = []
            
            # Project cards typically have links with class 'link-to-software'
            project_links = soup.find_all('a', class_='link-to-software')
            
            for link in project_links:
                project_url = link.get('href')
                if project_url and project_url.startswith('http'):
                    if project_url not in project_urls:  # Avoid duplicates
                        project_urls.append(project_url)
                        if max_projects and len(project_urls) >= max_projects:
                            break
            
            print(f"Found {len(project_urls)} project(s)")
            return project_urls
        
        except Exception as e:
            print(f"Error scraping gallery: {e}")
            return []
    
    def scrape_hackathon_schedule(self, hackathon_url: str) -> List[Dict[str, str]]:
        """
        Scrape a hackathon's schedule from the dates page.
        
        Args:
            hackathon_url: URL to the hackathon page (e.g., https://deltahacks-12.devpost.com/)
            
        Returns:
            List of schedule events with period, start_time, and end_time
        """
        try:
            # Build the schedule URL
            base_url = hackathon_url.rstrip('/')
            schedule_url = f"{base_url}/details/dates"
            
            print(f"Fetching schedule: {schedule_url}")
            response = self.session.get(schedule_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the schedule table
            schedule_table = soup.find('table', class_='no-borders')
            if not schedule_table:
                print("Schedule table not found")
                return []
            
            # Extract schedule events
            schedule = []
            tbody = schedule_table.find('tbody')
            if tbody:
                rows = tbody.find_all('tr')
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 3:
                        period = cells[0].text.strip()
                        start_time = cells[1].get('data-iso-date', cells[1].text.strip())
                        end_time = cells[2].get('data-iso-date', cells[2].text.strip())
                        
                        schedule.append({
                            'period': period,
                            'start_time': start_time,
                            'end_time': end_time
                        })
            
            print(f"Found {len(schedule)} schedule event(s)")
            return schedule
        
        except Exception as e:
            print(f"Error scraping schedule: {e}")
            return []
    
    def scrape_project(self, url: str) -> Dict:
        """
        Scrape a single Devpost project page.
        
        Args:
            url: Full URL to the Devpost project page
            
        Returns:
            Dictionary containing extracted project data
        """
        try:
            response = self.session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            return {
                'url': url,
                'title': self._extract_title(soup),
                'tagline': self._extract_tagline(soup),
                'story': self._extract_story(soup),
                'built_with': self._extract_technologies(soup),
                'links': self._extract_links(soup),
                'github_repo': self._extract_github_link(soup),
                'team_members': self._extract_team(soup),
                'hackathon': self._extract_hackathon(soup),
                'prizes': self._extract_prizes(soup)
            }
        
        except Exception as e:
            return {'error': str(e), 'url': url}
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract project title."""
        title_tag = soup.find('h1', id='app-title')
        return title_tag.text.strip() if title_tag else ''
    
    def _extract_tagline(self, soup: BeautifulSoup) -> str:
        """Extract project tagline/subtitle."""
        tagline_tag = soup.find('p', id='app-tagline')
        return tagline_tag.text.strip() if tagline_tag else ''
    
    def _extract_story(self, soup: BeautifulSoup) -> Dict[str, str]:
        """
        Extract the project story sections.
        Typically includes: Inspiration, What it does, How we built it, etc.
        """
        story = {}
        
        # Find the main content area
        content_div = soup.find('div', id='app-details-left')
        if not content_div:
            return story
        
        # Look for standard Devpost story sections
        sections = content_div.find_all(['h2', 'h3', 'p'])
        current_heading = None
        
        for element in sections:
            if element.name in ['h2', 'h3']:
                current_heading = element.text.strip()
                story[current_heading] = ''
            elif element.name == 'p' and current_heading:
                story[current_heading] += element.text.strip() + '\n\n'
        
        return {k: v.strip() for k, v in story.items() if v.strip()}
    
    def _extract_technologies(self, soup: BeautifulSoup) -> List[str]:
        """Extract 'Built With' technologies/tags."""
        tech_tags = soup.find_all('span', class_='cp-tag')
        return [tag.text.strip() for tag in tech_tags]
    
    def _extract_links(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract all external links (demos, videos, etc.)."""
        links = []
        
        # Find the links section
        links_section = soup.find('div', id='app-links')
        if links_section:
            link_elements = links_section.find_all('a', class_='link-to-software')
            for link in link_elements:
                links.append({
                    'url': link.get('href', ''),
                    'text': link.text.strip()
                })
        
        return links
    
    def _extract_github_link(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract GitHub repository link if present."""
        # Check in the links section
        links_section = soup.find('div', id='app-links')
        if links_section:
            github_link = links_section.find('a', href=re.compile(r'github\.com'))
            if github_link:
                return github_link.get('href')
        
        # Also check in the story content
        content_div = soup.find('div', id='app-details-left')
        if content_div:
            github_link = content_div.find('a', href=re.compile(r'github\.com'))
            if github_link:
                return github_link.get('href')
        
        return None
    
    def _extract_team(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract team member information."""
        team = []
        
        # Team section is a <section> not a <div>
        team_section = soup.find('section', id='app-team')
        if team_section:
            members = team_section.find_all('li', class_='software-team-member')
            for member in members:
                # There are two links per member - one for avatar, one for name
                # Get all links and find the one with text content (the name link)
                links = member.find_all('a', class_='user-profile-link')
                name_tag = None
                for link in links:
                    if link.text.strip():  # This is the text link, not the image link
                        name_tag = link
                        break
                
                if name_tag:
                    team.append({
                        'name': name_tag.text.strip(),
                        'profile_url': name_tag.get('href', '')
                    })
        
        return team
    
    def _extract_hackathon(self, soup: BeautifulSoup) -> str:
        """Extract the hackathon name this project was submitted to."""
        hackathon_tag = soup.find('a', id='parent_hackathon_link')
        return hackathon_tag.text.strip() if hackathon_tag else ''
    
    def _extract_prizes(self, soup: BeautifulSoup) -> List[str]:
        """Extract any prizes won."""
        prizes = []
        
        # Find prize badges/labels
        prize_section = soup.find('div', id='gallery-sub-nav')
        if prize_section:
            prize_tags = prize_section.find_all('span', class_='winner-prize')
            prizes = [tag.text.strip() for tag in prize_tags]
        
        return prizes


def save_to_json(data: Dict, filename: str):
    """Save extracted data to a JSON file."""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


if __name__ == '__main__':
    # Example usage
    scraper = DevpostScraper()
    
    # Test with the deltawash project from DeltaHacks 12
    project_url = 'https://devpost.com/software/fleetguard'
    
    print(f"Scraping: {project_url}")
    project_data = scraper.scrape_project(project_url)
    
    if 'error' in project_data:
        print(f"Error: {project_data['error']}")
    else:
        print(f"\n{'='*60}")
        print(f"Title: {project_data['title']}")
        print(f"Tagline: {project_data['tagline']}")
        print(f"Hackathon: {project_data['hackathon']}")
        print(f"Technologies: {', '.join(project_data['built_with'])}")
        print(f"GitHub: {project_data['github_repo']}")
        print(f"Team Size: {len(project_data['team_members'])}")
        print(f"\nStory Sections: {list(project_data['story'].keys())}")
        print(f"{'='*60}\n")
        
        # Save to file
        save_to_json(project_data, 'output/sample_project.json')
        print("Data saved to output/sample_project.json")
