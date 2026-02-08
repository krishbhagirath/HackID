"""
Validation Pipeline
Orchestrates both agents to validate a Devpost project.
Now uses Gemini + GitHub API with minimal requests.
"""

from agents.claim_extractor import ClaimExtractor
from agents.github_validator import GitHubValidator
from scraper import DevpostScraper
from database import SessionLocal, Hackathon, Project
import json
import os
from sqlalchemy.dialects.postgresql import insert


class ValidationPipeline:
    """Complete validation pipeline combining both agents."""
    
    def __init__(self, google_api_key: str, github_token: str = None):
        self.claim_extractor = ClaimExtractor(api_key=google_api_key)
        self.github_validator = GitHubValidator(
            github_token=github_token,
            llm=self.claim_extractor.llm
        )
    
    def save_to_supabase(self, org_id: str, hackathon_url: str, devpost_data: dict, result: dict):
        """
        Save hackathon and project result to Supabase.
        """
        db = SessionLocal()
        try:
            # 1. Upsert Hackathon (using devpost_url as unique key)
            # We strip trailing slash for consistency
            clean_hackathon_url = hackathon_url.rstrip('/')
            
            # Using SQLAlchemy ORM for better compatibility with UUID generators
            hackathon = db.query(Hackathon).filter(Hackathon.devpost_url == clean_hackathon_url).first()
            
            if not hackathon:
                hackathon = Hackathon(
                    org_id=org_id,
                    name=devpost_data.get('hackathon') or "Unnamed Hackathon",
                    devpost_url=clean_hackathon_url,
                    start_time=devpost_data.get('start_time'),
                    end_time=devpost_data.get('end_time')
                )
                db.add(hackathon)
                db.flush() # Get the generated hackathon_id
            else:
                # Update existing hackathon if data changed
                hackathon.name = devpost_data.get('hackathon') or hackathon.name
                hackathon.start_time = devpost_data.get('start_time') or hackathon.start_time
                hackathon.end_time = devpost_data.get('end_time') or hackathon.end_time
            
            # 2. Save Project
            project = Project(
                hackathon_id=hackathon.hackathon_id,
                source_url=devpost_data.get('url'),
                title=devpost_data.get('title'),
                github_repo_link=devpost_data.get('github_repo'),
                data=result # Store full validation JSON
            )
            db.add(project)
            db.commit()
            print(f"   ✓ Saved to Supabase: {devpost_data['title']}")
            
        except Exception as e:
            db.rollback()
            print(f"   ✗ Database error: {str(e)}")
        finally:
            db.close()
    
    def validate_project(self, devpost_data: dict) -> dict:
        """
        Complete validation pipeline.
        
        Args:
            devpost_data: Your scraper's JSON output
        
        Returns:
            Full validation report with clear descriptions
        """
        
        print(f"\n{'='*70}")
        print(f"🔬 HackID Validation: {devpost_data['title']}")
        print(f"{'='*70}\n")
        
        # Step 1: Extract claims
        print("📋 STEP 1/2: Extracting claims from Devpost...")
        try:
            claims = self.claim_extractor.extract_claims(devpost_data)
            print(f"   ✓ Found {len(claims.tech_stack)} technologies")
            print(f"   ✓ Found {len(claims.key_features)} features")
            print(f"   ✓ Found {len(claims.team_members)} team members\n")
        except Exception as e:
            return {
                "final_status": "ERROR",
                "error": f"Claim extraction failed: {str(e)}",
                "project_title": devpost_data['title'],
                "description": "❌ Failed to extract claims from Devpost"
            }
        
        # Step 2: Validate GitHub
        github_url = devpost_data.get('github_repo')
        if not github_url:
            return {
                "final_status": "ERROR",
                "error": "No GitHub repository found in Devpost",
                "project_title": devpost_data['title'],
                "description": "❌ No GitHub repository linked to this project"
            }
        
        print("🔍 STEP 2/2: Validating GitHub repository...")
        try:
            report = self.github_validator.validate_project(
                github_url=github_url,
                claims=claims.model_dump(),
                hackathon_start=devpost_data['start_time'],
                hackathon_end=devpost_data['end_time']
            )
        except Exception as e:
            return {
                "final_status": "ERROR",
                "error": f"GitHub validation failed: {str(e)}",
                "project_title": devpost_data['title'],
                "description": f"❌ Failed to access GitHub: {str(e)}"
            }
        
        # Prepare final reasoning
        reasoning = self._generate_reasoning(report, claims.model_dump())
        
        # Generate detailed description
        description = self._generate_description(report, claims.model_dump())
        
        # Combine results
        return {
            "project_title": devpost_data['title'],
            "project_url": devpost_data['url'],
            "github_url": github_url,
            "final_status": report.status,
            "reasoning": reasoning,
            "confidence": report.confidence,
            "claims": claims.model_dump(),
            "validation": report.model_dump(),
            "flags": report.flags,
            "api_calls_used": report.api_calls_used,
            "description": description
        }
    
    def _generate_description(self, report, claims) -> str:
        """Generate human-readable description of validation results."""
        
        lines = []
        
        # Status header
        if report.status == "DISQUALIFIED":
            lines.append("🚫 **DISQUALIFIED**")
            lines.append("This project has NO commits during the hackathon timeframe.")
            lines.append(f"Hackathon commits: {report.commits_in_timeframe}")
            lines.append(f"Outside commits: {report.commits_outside_timeframe}")
            return "\n".join(lines)
        
        elif report.status == "VERIFIED":
            lines.append(f"✅ **VERIFIED** (Confidence: {report.confidence:.0%})")
            lines.append("All checks passed!")
        
        else:  # FLAGGED
            lines.append(f"🚩 **FLAGGED FOR REVIEW** (Confidence: {report.confidence:.0%})")
            lines.append(f"Found {len(report.flags)} issue(s) requiring manual review.")
        
        lines.append("")
        
        # Tech stack (Highlight Core)
        core_techs = [t['name'] for t in claims['tech_stack'] if t['weight'] >= 1.0]
        
        lines.append(f"📦 **Tech Stack:** {len(report.tech_found)}/{len(claims['tech_stack'])} verified")
        
        # Display Core
        if core_techs:
            found_core = [t for t in core_techs if t in report.tech_found]
            missing_core = [t for t in core_techs if t not in report.tech_found]
            lines.append(f"   🔹 **Core:** {len(found_core)}/{len(core_techs)} found")
            if missing_core:
                lines.append(f"      ✗ Missing Core: {', '.join(missing_core)}")
        
        if report.tech_found:
            lines.append(f"   ✓ Found: {', '.join(report.tech_found)}")
        
        # Only list missing if they aren't core (already listed)
        non_core_missing = [t for t in report.tech_missing if t not in core_techs]
        if non_core_missing:
            lines.append(f"   ℹ️  Note: Minor/Secondary tech not found: {', '.join(non_core_missing)}")
        
        lines.append("")
        
        # Team (Information Only)
        lines.append(f"👥 **Team:** {len(claims['team_members'])} claimed members")
        if report.team_matched:
            lines.append(f"   ✓ Commits found for: {', '.join(report.team_matched)}")
        if report.team_unmatched:
            lines.append(f"   ℹ️  No commits seen for: {', '.join(report.team_unmatched)}")
        if report.unauthorized_contributors:
            lines.append(f"   ℹ️  Other contributors: {', '.join(report.unauthorized_contributors)}")
        
        lines.append("")
        
        # Timeline
        total = report.commits_in_timeframe + report.commits_outside_timeframe
        lines.append(f"⏰ **Timeline:** {report.commits_in_timeframe}/{total} commits during hackathon")
        
        lines.append("")
        lines.append(f"📊 **API Calls Used:** {report.api_calls_used}")
        
        return "\n".join(lines)

    def _generate_reasoning(self, report, claims) -> str:
        """Generate 1-2 sentence concise reasoning for the validation decision."""
        status = report.status
        
        if status == "VERIFIED":
            if report.flags:
                # Still verified, but noting minor flags (like Leeway or minor tech)
                return f"Project verified with {report.confidence:.0%} confidence. Core requirements met (minor notes: {'; '.join(report.flags)})."
            return f"Project verified with {report.confidence:.0%} confidence. All technologies found and commits started after the hackathon began."
        
        elif status == "DISQUALIFIED":
            if report.commits_in_timeframe == 0:
                return "Disqualified: No work found within the hackathon timeframe."
            if any("BEFORE" in f for f in report.flags):
                return f"Disqualified: Found {report.commits_outside_timeframe} commits made before the hackathon started (Violation of core timeline rule)."
            return "Disqualified: Project failed basic eligibility checks."
            
        else: # FLAGGED
            core_missing = [t['name'] for t in claims['tech_stack'] if t['name'] in report.tech_missing and t['weight'] >= 1.0]
            if core_missing:
                return f"Flagged: Missing {len(core_missing)} CORE technologies ({', '.join(core_missing)}). Manual review required."
            
            # This should rarely happen with the new GitHubValidator logic
            if report.flags:
                return f"Flagged for review: {'; '.join(report.flags)}."
            return "Flagged for manual review."
    
    def validate_from_url(
        self,
        devpost_url: str,
        hackathon_url: str,
        org_id: str = None,
        save_artifacts: bool = False
    ) -> dict:
        """
        Complete validation from Devpost URL to report (deployment-ready).
        
        Args:
            devpost_url: Devpost project URL
            hackathon_url: Hackathon page URL (for dates)
            save_artifacts: Optional - save JSON files for debugging
        
        Returns:
            Validation report dict
        """
        
        print(f"\n{'='*70}")
        print(f"🌐 URL-Based Validation")
        print(f"{'='*70}\n")
        
        # Step 0a: Scrape project
        print(f"📥 Scraping Devpost: {devpost_url}")
        scraper = DevpostScraper()
        devpost_data = scraper.scrape_project(devpost_url)
        
        if 'error' in devpost_data:
            return {
                "final_status": "ERROR",
                "error": f"Failed to scrape Devpost: {devpost_data['error']}",
                "project_url": devpost_url,
                "project_title": "Scrape Error",
                "description": "❌ Could not access Devpost project page"
            }
        
        print(f"   ✓ Scraped: {devpost_data['title']}\n")
        
        # Step 0b: Get hackathon dates
        print(f"📅 Fetching hackathon schedule: {hackathon_url}")
        schedule = scraper.scrape_hackathon_schedule(hackathon_url)
        
        if not schedule:
            return {
                "final_status": "ERROR",
                "error": "Failed to fetch hackathon schedule",
                "project_title": devpost_data['title'],
                "description": "❌ Could not determine hackathon dates"
            }
        
        start_time, end_time = self._extract_hackathon_dates(schedule)
        devpost_data['start_time'] = start_time
        devpost_data['end_time'] = end_time
        print(f"   ✓ Hackathon period: {start_time} to {end_time}\n")
        
        # Step 1-2: Validate using existing pipeline
        result = self.validate_project(devpost_data)
        
        # Step 3: Save to Supabase (if org_id provided)
        if org_id:
            self.save_to_supabase(
                org_id=org_id,
                hackathon_url=hackathon_url,
                devpost_data=devpost_data,
                result=result
            )
        
        # Optional: Save artifacts for debugging
        if save_artifacts:
            from pathlib import Path
            output_dir = Path('output')
            output_dir.mkdir(exist_ok=True)
            
            # Create slug from title
            slug = devpost_data['title'].lower().replace(' ', '-').replace('/', '-')
            
            with open(output_dir / f"{slug}.json", 'w', encoding='utf-8') as f:
                json.dump(devpost_data, f, indent=2, ensure_ascii=False)
            
            with open(output_dir / f"{slug}_validation.json", 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            print(f"\n💾 Debug files saved to output/")
        
        return result
    
    def _extract_hackathon_dates(self, schedule: list) -> tuple:
        """
        Extract start and end times from hackathon schedule.
        Looks for 'Submissions' period.
        
        Returns:
            (start_time, end_time) in ISO format
        """
        # Look for submission period
        for event in schedule:
            period = event.get('period', '').lower()
            if 'submission' in period:
                return event['start_time'], event['end_time']
        
        # Fallback: use first and last events
        if schedule:
            return schedule[0]['start_time'], schedule[-1]['end_time']
        
        raise ValueError("No submission period found in hackathon schedule")
    
    def validate_hackathon(
        self,
        hackathon_url: str,
        org_id: str = None,
        max_projects: int = None,
        delay_seconds: float = 4.0,
        save_artifacts: bool = False
    ) -> list:
        """
        Validate all (or N) projects from a hackathon gallery.
        
        Args:
            hackathon_url: Hackathon page URL (e.g., https://deltahacks-12.devpost.com)
            max_projects: Optional limit (None = all projects)
            delay_seconds: Delay between projects to avoid rate limits
            save_artifacts: Save JSON files for each project
        
        Returns:
            List of validation reports
        """
        import time
        
        print(f"\n{'='*70}")
        print(f"🎯 BATCH VALIDATION: {hackathon_url}")
        print(f"{'='*70}\n")
        
        # Step 1: Get all project URLs from gallery
        scraper = DevpostScraper()
        print(f"📥 Fetching project gallery...")
        project_urls = scraper.scrape_hackathon_gallery(hackathon_url, max_projects)
        
        if not project_urls:
            print("❌ No projects found in gallery")
            return []
        
        print(f"✓ Found {len(project_urls)} project(s) to validate\n")
        
        # Step 2: Validate each project
        results = []
        for i, project_url in enumerate(project_urls, 1):
            print(f"\n{'─'*70}")
            print(f"Project {i}/{len(project_urls)}")
            print(f"{'─'*70}")
            
            try:
                result = self.validate_from_url(
                    devpost_url=project_url,
                    hackathon_url=hackathon_url,
                    org_id=org_id,
                    save_artifacts=save_artifacts
                )
                results.append(result)
                
                # Summary
                status_emoji = {
                    "VERIFIED": "✅",
                    "FLAGGED": "🚩",
                    "DISQUALIFIED": "❌",
                    "ERROR": "⚠️"
                }.get(result.get('final_status', 'ERROR'), "❓")
                
                print(f"\n{status_emoji} {result.get('project_title', 'Unknown')}: {result.get('final_status', 'ERROR')}")
                print(f"   Reason: {result.get('reasoning', 'No reasoning provided.')}")
                
            except Exception as e:
                print(f"❌ Validation failed: {str(e)}")
                results.append({
                    "project_url": project_url,
                    "status": "ERROR",
                    "error": str(e)
                })
            
            # Rate limiting delay (except for last project)
            if i < len(project_urls):
                print(f"\n⏳ Waiting {delay_seconds}s before next project...")
                time.sleep(delay_seconds)
        
        # Final summary
        print(f"\n{'='*70}")
        print(f"📊 BATCH COMPLETE: {len(results)} projects processed")
        print(f"{'='*70}")
        
        verified = sum(1 for r in results if r.get('final_status') == 'VERIFIED')
        flagged = sum(1 for r in results if r.get('final_status') == 'FLAGGED')
        disqualified = sum(1 for r in results if r.get('final_status') == 'DISQUALIFIED')
        errors = sum(1 for r in results if r.get('final_status') == 'ERROR')
        
        print(f"✅ Verified: {verified}")
        print(f"🚩 Flagged: {flagged}")
        print(f"❌ Disqualified: {disqualified}")
        print(f"⚠️  Errors: {errors}")
        print(f"{'='*70}\n")
        
        return results
    
    def validate_batch(self, devpost_projects: list) -> list:
        """
        Validate multiple projects at once.
        
        Args:
            devpost_projects: List of Devpost JSON objects
        
        Returns:
            List of validation reports
        """
        
        results = []
        total_api_calls = 0
        
        for i, project in enumerate(devpost_projects, 1):
            if i > 1:
                print(f"⏳ Waiting 30s to respect API rate limits...")
                import time
                time.sleep(30)
                
            print(f"\n{'='*70}")
            print(f"📊 Project {i}/{len(devpost_projects)}")
            print(f"{'='*70}")
            
            result = self.validate_project(project)
            results.append(result)
            total_api_calls += result.get('api_calls_used', 0)
            
            print(f"\n✅ Result: {result['final_status']}")
            if result.get('flags'):
                print(f"🚩 Flags: {len(result['flags'])}")
        
        print(f"\n{'='*70}")
        print(f"📊 BATCH SUMMARY")
        print(f"{'='*70}")
        print(f"Total Projects: {len(devpost_projects)}")
        print(f"Total API Calls: {total_api_calls}")
        print(f"Average per Project: {total_api_calls / len(devpost_projects):.1f}")
        
        return results


# Test the pipeline
if __name__ == "__main__":
    from dotenv import load_dotenv
    from pathlib import Path
    import sys
    import glob
    
    env_path = Path(__file__).parent.parent / ".env"
    load_dotenv(dotenv_path=env_path)
    
    # Check for API keys
    google_key = os.getenv('GOOGLE_API_KEY')
    github_token = os.getenv('GITHUB_TOKEN')
    
    if not google_key:
        print("❌ GOOGLE_API_KEY not set in .env")
        exit(1)
    
    if github_token == "your-github-token-here-optional" or not github_token:
        print("⚠️  Using GitHub public rate limit (60 req/hr). Add real GITHUB_TOKEN for 5,000 req/hr.")
        github_token = None
    
    # Create pipeline
    pipeline = ValidationPipeline(
        google_api_key=google_key,
        github_token=github_token
    )
    
    # Argument handling
    output_dir = Path(__file__).parent.parent / "output"
    
    if len(sys.argv) > 1:
        target = sys.argv[1]
        
        if target.lower() == "all":
            # Batch validate all project JSONs
            projects = []
            file_paths = glob.glob(str(output_dir / "*.json"))
            # Filter out the combined summary files
            file_paths = [f for f in file_paths if "all_" not in f]
            
            for f_path in file_paths:
                with open(f_path, 'r', encoding='utf-8') as f:
                    projects.append(json.load(f))
            
            print(f"🚀 Batch validating {len(projects)} projects...")
            results = pipeline.validate_batch(projects)
            print(f"\n✅ Batch validation complete. Results printed above.")
            
        elif target.lower() == "gallery":
            # Batch validate from Devpost gallery URL
            if len(sys.argv) < 3:
                print("Usage: python pipeline.py gallery <hackathon_url> [--max <number>]")
                exit(1)
            
            hackathon_url = sys.argv[2]
            max_projects = None
            if "--max" in sys.argv:
                max_idx = sys.argv.index("--max")
                if len(sys.argv) > max_idx + 1:
                    max_projects = int(sys.argv[max_idx + 1])
            
            print(f"🚀 Batch validating from gallery: {hackathon_url}")
            results = pipeline.validate_hackathon(
                hackathon_url=hackathon_url,
                max_projects=max_projects,
                save_artifacts=False # Do not save raw scrapes as per user request
            )
            print(f"\n✅ Gallery validation complete. Results printed above.")

        else:
            # Single project validation
            project_file = output_dir / target
            if not project_file.suffix:
                project_file = project_file.with_suffix('.json')
                
            if not project_file.exists():
                print(f"❌ Project file not found: {project_file}")
                exit(1)
                
            with open(project_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            result = pipeline.validate_project(data)
            
            print(f"\n{'='*70}")
            print("📋 VALIDATION REPORT")
            print(f"{'='*70}\n")
            print(result['description'])
            if result.get('flags'):
                print(f"\n🚩 Flags: {len(result['flags'])}")
    else:
        print("Usage:")
        print("  python pipeline.py <project_name> (e.g. bloomguard)")
        print("  python pipeline.py all")
        
        # Default fallback to LavaLock for convenience
        test_file = output_dir / 'lavalock.json'
        if test_file.exists():
            print(f"\nRunning default test on {test_file.name}...\n")
            with open(test_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            pipeline.validate_project(data)
