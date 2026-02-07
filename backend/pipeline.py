"""
Validation Pipeline
Orchestrates both agents to validate a Devpost project.
Now uses Gemini + GitHub API with minimal requests.
"""

from agents.claim_extractor import ClaimExtractor
from agents.github_validator import GitHubValidator
import json
import os


class ValidationPipeline:
    """Complete validation pipeline combining both agents."""
    
    def __init__(self, google_api_key: str, github_token: str = None):
        self.claim_extractor = ClaimExtractor(api_key=google_api_key)
        self.github_validator = GitHubValidator(github_token=github_token)
    
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
                "status": "ERROR",
                "error": f"Claim extraction failed: {str(e)}",
                "project": devpost_data['title'],
                "description": "❌ Failed to extract claims from Devpost"
            }
        
        # Step 2: Validate GitHub
        github_url = devpost_data.get('github_repo')
        if not github_url:
            return {
                "status": "ERROR",
                "error": "No GitHub repository found in Devpost",
                "project": devpost_data['title'],
                "description": "❌ No GitHub repository linked to this project"
            }
        
        print("🔍 STEP 2/2: Validating GitHub repository...")
        try:
            report = self.github_validator.validate_project(
                github_url=github_url,
                claims=claims.dict(),
                hackathon_start=devpost_data['start_time'],
                hackathon_end=devpost_data['end_time']
            )
        except Exception as e:
            return {
                "status": "ERROR",
                "error": f"GitHub validation failed: {str(e)}",
                "project": devpost_data['title'],
                "description": f"❌ Failed to access GitHub: {str(e)}"
            }
        
        # Generate human-readable description
        description = self._generate_description(report, claims.dict())
        
        # Combine results
        return {
            "project_title": devpost_data['title'],
            "project_url": devpost_data['url'],
            "github_url": github_url,
            "claims": claims.dict(),
            "validation": report.dict(),
            "final_status": report.status,
            "confidence": report.confidence,
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
        
        # Tech stack
        lines.append(f"📦 **Tech Stack:** {len(report.tech_found)}/{len(claims['tech_stack'])} verified")
        if report.tech_found:
            lines.append(f"   ✓ Found: {', '.join(report.tech_found)}")
        if report.tech_missing:
            lines.append(f"   ✗ Missing: {', '.join(report.tech_missing)}")
        
        lines.append("")
        
        # Team
        lines.append(f"👥 **Team:** {len(report.team_matched)}/{len(claims['team_members'])} verified")
        if report.team_matched:
            lines.append(f"   ✓ Matched: {', '.join(report.team_matched)}")
        if report.team_unmatched:
            lines.append(f"   ✗ Not found: {', '.join(report.team_unmatched)}")
        if report.unauthorized_contributors:
            lines.append(f"   ⚠️  Unauthorized: {', '.join(report.unauthorized_contributors)}")
        
        lines.append("")
        
        # Timeline
        total = report.commits_in_timeframe + report.commits_outside_timeframe
        lines.append(f"⏰ **Timeline:** {report.commits_in_timeframe}/{total} commits during hackathon")
        
        lines.append("")
        lines.append(f"📊 **API Calls Used:** {report.api_calls_used}")
        
        return "\n".join(lines)
    
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
    
    load_dotenv()
    
    # Load scraped project
    test_file = Path('../output/lavalock.json')
    
    if not test_file.exists():
        print(f"❌ Test file not found: {test_file}")
        print("Run the Devpost scraper first!")
        exit(1)
    
    with open(test_file, 'r') as f:
        devpost_data = json.load(f)
    
    # Check for API keys
    google_key = os.getenv('GOOGLE_API_KEY')
    github_token = os.getenv('GITHUB_TOKEN')
    
    if not google_key:
        print("❌ GOOGLE_API_KEY not set in .env")
        exit(1)
    
    if not github_token:
        print("⚠️  GITHUB_TOKEN not set (will use 60 req/hr limit)")
    
    # Create pipeline
    pipeline = ValidationPipeline(
        google_api_key=google_key,
        github_token=github_token
    )
    
    # Run validation
    result = pipeline.validate_project(devpost_data)
    
    # Save result
    output_file = Path('validation_result.json')
    with open(output_file, 'w') as f:
        json.dump(result, indent=2, fp=f)
    
    # Print results
    print(f"\n{'='*70}")
    print("📋 VALIDATION REPORT")
    print(f"{'='*70}\n")
    
    print(result['description'])
    
    if result.get('flags'):
        print(f"\n🚩 **Flags:**")
        for i, flag in enumerate(result['flags'], 1):
            print(f"   {i}. {flag}")
    
    print(f"\n💾 Full report saved to: {output_file}")
    print(f"{'='*70}")
