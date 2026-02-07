"""
Agent 2: GitHub Validator
Validates Devpost claims against GitHub repository using GitHub API (no cloning).
Optimized for minimal API requests.
"""

from github import Github
from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel
import base64


class ValidationReport(BaseModel):
    """Complete validation report for a project."""
    status: str  # "VERIFIED", "FLAGGED", or "DISQUALIFIED"
    tech_found: List[str]
    tech_missing: List[str]
    team_matched: List[str]
    team_unmatched: List[str]
    unauthorized_contributors: List[str]
    commits_in_timeframe: int
    commits_outside_timeframe: int
    first_commit: Optional[str]
    last_commit: Optional[str]
    flags: List[str]
    confidence: float
    api_calls_used: int  # Track API usage


class GitHubValidator:
    """Agent 2: Validates claims against GitHub repository using API only."""
    
    def __init__(self, github_token: Optional[str] = None):
        self.github = Github(github_token) if github_token else Github()
        self.api_calls = 0  # Track API usage
        
        # Tech detection patterns (file names to look for)
        self.tech_files = {
            "React": ["package.json"],
            "Python": ["requirements.txt", "setup.py", "pyproject.toml"],
            "Node.js": ["package.json"],
            "Express": ["package.json"],
            "MongoDB": ["package.json", "requirements.txt"],
            "PostgreSQL": ["requirements.txt", "package.json"],
            "AWS": ["requirements.txt", "package.json"],
            "Firebase": ["package.json"],
            "C++": [],  # Will check languages API
            "C": [],
            "Go": ["go.mod", "go.sum"],
            "Swift": [],
            "TypeScript": ["package.json", "tsconfig.json"],
            "Tailwind": ["package.json", "tailwind.config.js"],
            "Next.js": ["next.config.js", "package.json"],
            "Flask": ["requirements.txt"],
            "FastAPI": ["requirements.txt"],
            "Gemini": ["requirements.txt", "package.json"],
            "Gemini API": ["requirements.txt", "package.json"],
            "OpenAI": ["requirements.txt", "package.json"],
            "ESP32": [],
            "Arduino": [],
            "OpenCV": ["requirements.txt"],
        }
        
        # Tech keywords to search in files
        self.tech_keywords = {
            "React": ["react", "react-dom"],
            "Express": ["express"],
            "MongoDB": ["mongodb", "mongoose"],
            "PostgreSQL": ["psycopg2", "pg", "postgres"],
            "AWS": ["boto3", "aws-sdk", "amazonaws"],
            "Firebase": ["firebase"],
            "TypeScript": ["typescript"],
            "Tailwind": ["tailwindcss"],
            "Next.js": ["next"],
            "Flask": ["flask"],
            "FastAPI": ["fastapi"],
            "Gemini": ["google-generativeai", "gemini"],
            "Gemini API": ["google-generativeai", "gemini"],
            "OpenAI": ["openai"],
            "OpenCV": ["opencv", "cv2"],
        }
    
    def validate_project(
        self,
        github_url: str,
        claims: dict,
        hackathon_start: str,
        hackathon_end: str
    ) -> ValidationReport:
        """
        Main validation pipeline with minimal API calls.
        
        Args:
            github_url: GitHub repository URL
            claims: Output from Agent 1 (claim extractor)
            hackathon_start: ISO timestamp
            hackathon_end: ISO timestamp
        
        Returns:
            ValidationReport with all findings
        """
        
        self.api_calls = 0
        print(f"🔍 Validating: {github_url}")
        
        # Parse repo from URL
        try:
            repo_name = self._parse_repo_name(github_url)
            repo = self.github.get_repo(repo_name)
            self.api_calls += 1
        except Exception as e:
            return self._create_error_report(f"Failed to access repository: {str(e)}")
        
        # STEP 1: Timeline validation (DISQUALIFICATION CHECK)
        print("⏰ Checking commit timeline (CRITICAL)...")
        time_data = self._validate_timeline(repo, hackathon_start, hackathon_end)
        
        # IMMEDIATE DISQUALIFICATION if no commits in timeframe
        if time_data['in_timeframe'] == 0:
            return ValidationReport(
                status="DISQUALIFIED",
                tech_found=[],
                tech_missing=claims.get('tech_stack', []),
                team_matched=[],
                team_unmatched=claims.get('team_members', []),
                unauthorized_contributors=[],
                commits_in_timeframe=0,
                commits_outside_timeframe=time_data['outside_timeframe'],
                first_commit=time_data['first_commit'],
                last_commit=time_data['last_commit'],
                flags=["❌ DISQUALIFIED: No commits during hackathon timeframe"],
                confidence=0.0,
                api_calls_used=self.api_calls
            )
        
        # STEP 2: Tech stack validation
        print("📦 Checking tech stack...")
        tech_found, tech_missing = self._validate_tech_stack(
            repo,
            claims.get('tech_stack', [])
        )
        
        # STEP 3: Team validation
        print("👥 Checking team members...")
        team_matched, team_unmatched, unauthorized = self._validate_team(
            repo,
            claims.get('team_members', []),
            hackathon_start,
            hackathon_end
        )
        
        # Collect flags
        flags = self._collect_flags(
            tech_missing,
            team_unmatched,
            unauthorized,
            time_data
        )
        
        # Determine status
        status = "VERIFIED" if len(flags) == 0 else "FLAGGED"
        
        # Calculate confidence
        confidence = self._calculate_confidence(
            len(tech_found),
            len(tech_missing),
            len(team_matched),
            len(team_unmatched),
            time_data['in_timeframe'],
            time_data['outside_timeframe']
        )
        
        print(f"✅ Validation complete. API calls used: {self.api_calls}")
        
        return ValidationReport(
            status=status,
            tech_found=tech_found,
            tech_missing=tech_missing,
            team_matched=team_matched,
            team_unmatched=team_unmatched,
            unauthorized_contributors=unauthorized,
            commits_in_timeframe=time_data['in_timeframe'],
            commits_outside_timeframe=time_data['outside_timeframe'],
            first_commit=time_data['first_commit'],
            last_commit=time_data['last_commit'],
            flags=flags,
            confidence=confidence,
            api_calls_used=self.api_calls
        )
    
    def _parse_repo_name(self, github_url: str) -> str:
        """Extract owner/repo from GitHub URL."""
        # https://github.com/owner/repo or github.com/owner/repo
        parts = github_url.replace('https://', '').replace('http://', '').split('/')
        if 'github.com' in parts[0]:
            owner = parts[1]
            repo = parts[2].replace('.git', '')
            return f"{owner}/{repo}"
        raise ValueError(f"Invalid GitHub URL: {github_url}")
    
    def _validate_timeline(
        self,
        repo,
        hackathon_start: str,
        hackathon_end: str
    ) -> dict:
        """Check if commits were made during hackathon. (1-2 API calls)"""
        
        start_dt = datetime.fromisoformat(hackathon_start.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(hackathon_end.replace('Z', '+00:00'))
        
        try:
            # Get commits in timeframe (1 API call)
            commits_in = list(repo.get_commits(since=start_dt, until=end_dt))
            self.api_calls += 1
            
            # Get all commits to check outside timeframe (1 API call)
            all_commits = list(repo.get_commits())
            self.api_calls += 1
            
            in_timeframe = len(commits_in)
            outside_timeframe = len(all_commits) - in_timeframe
            
            if all_commits:
                commit_dates = [c.commit.author.date for c in all_commits]
                first_commit = min(commit_dates).isoformat()
                last_commit = max(commit_dates).isoformat()
            else:
                first_commit = None
                last_commit = None
            
            return {
                "in_timeframe": in_timeframe,
                "outside_timeframe": outside_timeframe,
                "first_commit": first_commit,
                "last_commit": last_commit
            }
        except Exception as e:
            print(f"⚠️  Timeline check error: {e}")
            return {
                "in_timeframe": 0,
                "outside_timeframe": 0,
                "first_commit": None,
                "last_commit": None
            }
    
    def _validate_tech_stack(
        self,
        repo,
        claimed_tech: List[str]
    ) -> tuple[List[str], List[str]]:
        """Check if claimed technologies exist. (2-5 API calls max)"""
        
        found = []
        
        # Get language breakdown (1 API call)
        try:
            languages = repo.get_languages()
            self.api_calls += 1
        except:
            languages = {}
        
        # Check languages first (free check)
        lang_map = {
            "C++": "C++",
            "C": "C",
            "Python": "Python",
            "JavaScript": "JavaScript",
            "TypeScript": "TypeScript",
            "Go": "Go",
            "Swift": "Swift"
        }
        
        for tech in claimed_tech:
            if tech in lang_map and lang_map[tech] in languages:
                found.append(tech)
        
        # For remaining tech, check config files (max 3-4 API calls)
        files_to_check = ["package.json", "requirements.txt", "go.mod"]
        file_contents = {}
        
        for filename in files_to_check:
            try:
                content = repo.get_contents(filename)
                file_contents[filename] = content.decoded_content.decode('utf-8')
                self.api_calls += 1
            except:
                pass  # File doesn't exist
        
        # Check tech keywords in files
        for tech in claimed_tech:
            if tech in found:
                continue  # Already found via languages
            
            keywords = self.tech_keywords.get(tech, [tech.lower()])
            
            for filename, content in file_contents.items():
                content_lower = content.lower()
                if any(kw in content_lower for kw in keywords):
                    found.append(tech)
                    break
        
        missing = [t for t in claimed_tech if t not in found]
        
        return found, missing
    
    def _validate_team(
        self,
        repo,
        claimed_members: List[str],
        hackathon_start: str,
        hackathon_end: str
    ) -> tuple[List[str], List[str], List[str]]:
        """Check if claimed team members contributed. (1 API call)"""
        
        start_dt = datetime.fromisoformat(hackathon_start.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(hackathon_end.replace('Z', '+00:00'))
        
        try:
            # Get commits during hackathon (already fetched in timeline, but re-use)
            commits = list(repo.get_commits(since=start_dt, until=end_dt))
            self.api_calls += 1
        except:
            return [], claimed_members, []
        
        # Count commits per contributor
        contributors = {}
        for commit in commits:
            author_name = commit.commit.author.name
            if author_name not in contributors:
                contributors[author_name] = 0
            contributors[author_name] += 1
        
        contributor_names = list(contributors.keys())
        
        # Match claimed members
        matched = []
        unmatched = []
        
        for claimed in claimed_members:
            if self._fuzzy_match_name(claimed, contributor_names):
                matched.append(claimed)
            else:
                unmatched.append(claimed)
        
        # Unauthorized contributors (>2 commits, not in team)
        unauthorized = [
            name for name, count in contributors.items()
            if count > 2 and not self._fuzzy_match_name(name, claimed_members)
        ]
        
        return matched, unmatched, unauthorized
    
    def _fuzzy_match_name(self, name: str, name_list: List[str]) -> bool:
        """Fuzzy match names (handles different formats)."""
        name_clean = name.lower().replace(' ', '').replace('-', '').replace('_', '')
        
        for candidate in name_list:
            candidate_clean = candidate.lower().replace(' ', '').replace('-', '').replace('_', '')
            
            if name_clean == candidate_clean:
                return True
            
            # Partial match (first or last name)
            if len(name_clean) >= 4 and len(candidate_clean) >= 4:
                if name_clean in candidate_clean or candidate_clean in name_clean:
                    return True
        
        return False
    
    def _collect_flags(
        self,
        tech_missing: List[str],
        team_unmatched: List[str],
        unauthorized: List[str],
        time_data: dict
    ) -> List[str]:
        """Collect all issues requiring manual review."""
        
        flags = []
        
        # Tech flags
        for tech in tech_missing:
            flags.append(f"Missing claimed technology: {tech}")
        
        # Team flags
        for member in team_unmatched:
            flags.append(f"Claimed member not found in commits: {member}")
        for contributor in unauthorized:
            flags.append(f"Unauthorized contributor found: {contributor}")
        
        # Time flags
        if time_data['outside_timeframe'] > time_data['in_timeframe']:
            flags.append(
                f"More commits outside ({time_data['outside_timeframe']}) "
                f"than inside ({time_data['in_timeframe']}) hackathon timeframe"
            )
        
        return flags
    
    def _calculate_confidence(
        self,
        tech_found: int,
        tech_missing: int,
        team_matched: int,
        team_unmatched: int,
        commits_in: int,
        commits_out: int
    ) -> float:
        """Calculate confidence score (0-1)."""
        
        scores = []
        
        # Tech score (40%)
        if tech_found + tech_missing > 0:
            tech_score = tech_found / (tech_found + tech_missing)
            scores.append(tech_score * 0.4)
        
        # Team score (30%)
        if team_matched + team_unmatched > 0:
            team_score = team_matched / (team_matched + team_unmatched)
            scores.append(team_score * 0.3)
        
        # Time score (30%)
        if commits_in + commits_out > 0:
            time_score = commits_in / (commits_in + commits_out)
            scores.append(time_score * 0.3)
        
        return sum(scores) if scores else 0.0
    
    def _create_error_report(self, error_message: str) -> ValidationReport:
        """Create error report when validation fails."""
        return ValidationReport(
            status="ERROR",
            tech_found=[],
            tech_missing=[],
            team_matched=[],
            team_unmatched=[],
            unauthorized_contributors=[],
            commits_in_timeframe=0,
            commits_outside_timeframe=0,
            first_commit=None,
            last_commit=None,
            flags=[error_message],
            confidence=0.0,
            api_calls_used=self.api_calls
        )


# Test directly
if __name__ == "__main__":
    import json
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    # Test with LavaLock project
    test_claims = {
        "tech_stack": ["AWS", "C", "C++", "ESP32", "Gemini API", "Go", "PostgreSQL", "Swift"],
        "team_members": ["Seoa Mo", "Kenny Zhao", "Anthony Hana", "Nathan Chan"]
    }
    
    validator = GitHubValidator(github_token=os.getenv('GITHUB_TOKEN'))
    
    print("="*60)
    print("Testing GitHub Validator (API Only - No Cloning)")
    print("="*60)
    
    report = validator.validate_project(
        github_url="https://github.com/anthonyhana04/Delta-Hacks-2026.git",
        claims=test_claims,
        hackathon_start="2026-01-10T11:00:00-05:00",
        hackathon_end="2026-01-11T11:00:00-05:00"
    )
    
    print("\n" + "="*60)
    print("VALIDATION REPORT")
    print("="*60)
    print(f"\nStatus: {report.status}")
    print(f"Confidence: {report.confidence:.1%}")
    print(f"API Calls Used: {report.api_calls_used}")
    
    print(f"\n📦 Tech Stack:")
    print(f"  Found: {report.tech_found}")
    print(f"  Missing: {report.tech_missing}")
    
    print(f"\n👥 Team:")
    print(f"  Matched: {report.team_matched}")
    print(f"  Unmatched: {report.team_unmatched}")
    print(f"  Unauthorized: {report.unauthorized_contributors}")
    
    print(f"\n⏰ Timeline:")
    print(f"  Commits in timeframe: {report.commits_in_timeframe}")
    print(f"  Commits outside: {report.commits_outside_timeframe}")
    
    print(f"\n🚩 Flags ({len(report.flags)}):")
    for flag in report.flags:
        print(f"  • {flag}")
    
    print(f"\n{'='*60}")
