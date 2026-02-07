import json
import os
from agents.claim_extractor import ClaimExtractor
from agents.github_validator import GitHubValidator
from dotenv import load_dotenv

load_dotenv(dotenv_path="../.env")

with open('../output/bloomguard.json', 'r') as f:
    data = json.load(f)

print(f"Data type: {type(data)}")
print(f"Data title: {data.get('title')}")

google_key = os.getenv('GOOGLE_API_KEY')
github_token = os.getenv('GITHUB_TOKEN')

extractor = ClaimExtractor(api_key=google_key)
validator = GitHubValidator(github_token=github_token)

try:
    print("Extracting claims...")
    claims = extractor.extract_claims(data)
    print(f"Claims type: {type(claims)}")
    
    print("Validating GitHub...")
    report = validator.validate_project(
        github_url=data['github_repo'],
        claims=claims.model_dump(),
        hackathon_start=data['start_time'],
        hackathon_end=data['end_time']
    )
    print(f"Report type: {type(report)}")
    print(f"Status: {report.status}")

except Exception as e:
    import traceback
    traceback.print_exc()
