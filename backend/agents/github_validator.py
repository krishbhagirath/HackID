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
    
    def __init__(self, github_token: Optional[str] = None, llm=None):
        self.github = Github(github_token) if github_token else Github()
        self.api_calls = 0  # Track API usage
        self.llm = llm # Gemini LLM for Tier 2 analysis
        
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
        
        # HARD DISQUALIFICATION: Any commit before start time
        if time_data['pre_start_commits'] > 0:
            return ValidationReport(
                status="DISQUALIFIED",
                tech_found=[],
                tech_missing=claims.get('tech_stack', []),
                team_matched=[],
                team_unmatched=claims.get('team_members', []),
                unauthorized_contributors=[],
                commits_in_timeframe=time_data['in_timeframe'],
                commits_outside_timeframe=time_data['outside_timeframe'],
                first_commit=time_data['first_commit'],
                last_commit=time_data['last_commit'],
                flags=[f"❌ DISQUALIFIED: Found {time_data['pre_start_commits']} commit(s) BEFORE hackathon started"],
                confidence=0.0,
                api_calls_used=self.api_calls
            )
        
        # DISQUALIFICATION if NO commits in timeframe (previously our only check)
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
                flags=["❌ DISQUALIFIED: No activity found during hackathon timeframe"],
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
            time_data['outside_timeframe'],
            time_data['leeway_commits']
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
        
        from datetime import timedelta
        
        start_dt = datetime.fromisoformat(hackathon_start.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(hackathon_end.replace('Z', '+00:00'))
        leeway_dt = end_dt + timedelta(hours=5)
        
        try:
            # Get all commits to check timeline (1 API call)
            all_commits = list(repo.get_commits())
            self.api_calls += 1
            
            pre_start = 0
            in_timeframe = 0
            leeway_commits = 0
            after_leeway = 0
            
            commit_dates = []
            for c in all_commits:
                dt = c.commit.author.date.replace(tzinfo=start_dt.tzinfo)
                commit_dates.append(dt)
                
                if dt < start_dt:
                    pre_start += 1
                elif start_dt <= dt <= end_dt:
                    in_timeframe += 1
                elif end_dt < dt <= leeway_dt:
                    leeway_commits += 1
                else:
                    after_leeway += 1
            
            first_commit = min(commit_dates).isoformat() if commit_dates else None
            last_commit = max(commit_dates).isoformat() if commit_dates else None
            
            return {
                "in_timeframe": in_timeframe,
                "pre_start_commits": pre_start,
                "leeway_commits": leeway_commits,
                "after_leeway_commits": after_leeway,
                "outside_timeframe": pre_start + leeway_commits, # We only care about suspect ones
                "first_commit": first_commit,
                "last_commit": last_commit
            }
        except Exception as e:
            print(f"⚠️  Timeline check error: {e}")
            return {
                "in_timeframe": 0,
                "pre_start_commits": 0,
                "leeway_commits": 0,
                "after_leeway_commits": 0,
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
        files_to_check = ["package.json", "requirements.txt", "go.mod", "pyproject.toml"]
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
        
        # TIER 2: Semantic Deep Dive for remaining missing tech
        missing = [t for t in claimed_tech if t not in found]
        if missing and self.llm:
            print(f"🕵️  Performing Tier 2 Deep Dive for: {missing}")
            # Batch all missing techs into one semantic check
            batch_found = self._semantic_deep_dive_batch(repo, missing)
            for tech in batch_found:
                if tech in missing:
                    found.append(tech)
                    missing.remove(tech)
        
        return found, missing

    def _semantic_deep_dive_batch(self, repo, techs: List[str]) -> List[str]:
        """Search for code snippets and use Gemini to verify multiple tech usage in one go. (3-5 API calls total)"""
        import time
        max_retries = 2
        
        # 1. Collect snippets for ALL missing techs (expensive in GitHub API calls, but saving LLM quota)
        all_snippets = []
        seen_paths = set()
        
        for tech in techs[:5]: # Limit to top 5 most important missing techs to save API
            try:
                keywords = self.tech_keywords.get(tech, [tech.lower()])
                query = f"repo:{repo.full_name} " + " OR ".join(keywords)
                search_results = self.github.search_code(query)
                self.api_calls += 1
                
                for i, result in enumerate(search_results):
                    if i >= 1 or result.path in seen_paths: continue
                    try:
                        content = base64.b64decode(result.content).decode('utf-8')
                        all_snippets.append(f"File: {result.path}\n```\n{content[:1000]}\n```")
                        seen_paths.add(result.path)
                        self.api_calls += 1
                    except:
                        continue
            except:
                continue

        if not all_snippets:
            return []
            
        # 2. Ask Gemini to verify ALL techs at once (1 LLM call)
        context = "\n\n".join(all_snippets)
        tech_list = ", ".join(techs)
        
        prompt = f"""You are a code auditor. A hackathon team claims to use these technologies: {tech_list}.
Review these code snippets from their repository and determine which ones are actually being used.

CODING CLUES:
{context}

Respond with a JSON list of technologies that are CLEARLY used. 
Format: {{"found": ["Tech1", "Tech2"]}}
"""

        for attempt in range(max_retries):
            try:
                response = self.llm.invoke(prompt)
                print(f"   🤖 Gemini Batch Audit: {response.content.strip()}")
                
                # Simple parsing (could use Pydantic but keeping it direct for Agent 2)
                import json
                try:
                    # Clean the JSON if Gemini wraps it in backticks
                    json_str = response.content.strip()
                    if "```json" in json_str:
                        json_str = json_str.split("```json")[1].split("```")[0].strip()
                    elif "```" in json_str:
                        json_str = json_str.split("```")[1].split("```")[0].strip()
                        
                    data = json.loads(json_str)
                    return data.get("found", [])
                except:
                    # Fallback to simple string check if JSON parsing fails
                    confirmed = [t for t in techs if t.upper() in response.content.upper()]
                    return confirmed
                    
            except Exception as e:
                if "429" in str(e) or "quota" in str(e).lower():
                    wait_time = 30 * (attempt + 1)
                    print(f"   ⏳ Rate limited during batch Tier 2. Waiting {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                print(f"   ⚠️  Batch deep dive failed: {e}")
                return []
        
        return []
    
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
        if time_data['pre_start_commits'] > 0:
            flags.append(f"❌ Hard Disqualification: {time_data['pre_start_commits']} commits BEFORE start")
            
        if time_data['leeway_commits'] > 0:
            flags.append(
                f"⚠️  Leeway Review: {time_data['leeway_commits']} commits "
                f"in the 5-hour post-deadline window"
            )
        
        return flags
    
    def _calculate_confidence(
        self,
        tech_found: int,
        tech_missing: int,
        team_matched: int,
        team_unmatched: int,
        commits_in: int,
        commits_out: int,
        leeway_commits: int = 0
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
        # Penalize leeway commits slightly (e.g., each leeway commit counts as 0.5 a normal commit for ratio)
        total_relevant = commits_in + leeway_commits
        if total_relevant > 0:
            time_score = commits_in / total_relevant
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
