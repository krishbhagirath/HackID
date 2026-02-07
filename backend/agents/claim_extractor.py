"""
Agent 1: Claim Extractor
Converts Devpost JSON into clean, testable claims using Gemini API.
"""

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List
import json


class ProjectClaims(BaseModel):
    """Structured claims extracted from a Devpost project."""
    
    tech_stack: List[str] = Field(
        description="Technologies claimed to be used (normalized names like 'React', 'Python', 'AWS')"
    )
    
    key_features: List[str] = Field(
        description="Main features/capabilities claimed in the project description"
    )
    
    team_members: List[str] = Field(
        description="Names of team members who worked on the project"
    )


class ClaimExtractor:
    """Agent 1: Extracts and normalizes claims from Devpost data."""
    
    def __init__(self, api_key: str):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0,
            api_key=api_key
        )
        
        self.parser = PydanticOutputParser(pydantic_object=ProjectClaims)
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a claim extraction agent for hackathon verification.

Extract testable claims from Devpost projects.

NORMALIZE TECHNOLOGY NAMES:
- "amazon-web-services" → "AWS"
- "c++" → "C++"
- "react" → "React"
- "node.js" → "Node.js"
- "next.js" → "Next.js"
- "typescript" → "TypeScript"
- "python" → "Python"
- "javascript" → "JavaScript"
- "opencv" → "OpenCV"
- "postgresql" → "PostgreSQL"
- "mongodb" → "MongoDB"

EXTRACT SPECIFIC FEATURES (be precise):
- GOOD: "Real-time chat", "File encryption with AES-256", "Camera motion detection"
- BAD: "Makes things easier", "Helps users", "Good UI"

Only extract what they CLAIM. Don't infer.

{format_instructions}"""),
            ("user", """Extract claims from this Devpost project:

Title: {title}

Technologies (built_with): {built_with}

Project Story:
{story}

Team Members: {team_members}""")
        ])
    
    def extract_claims(self, devpost_data: dict) -> ProjectClaims:
        """
        Extract claims from Devpost JSON.
        
        Args:
            devpost_data: Your existing scraper output
            
        Returns:
            ProjectClaims object with normalized claims
        """
        import time
        
        # Format the story sections
        story_text = "\n\n".join([
            f"{section}: {content}"
            for section, content in devpost_data.get('story', {}).items()
        ])
        
        # Format team members
        team_members = [member['name'] for member in devpost_data.get('team_members', [])]
        
        # Run the LLM with retry
        chain = self.prompt | self.llm | self.parser
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                result = chain.invoke({
                    "title": devpost_data.get('title', ''),
                    "built_with": ", ".join(devpost_data.get('built_with', [])),
                    "story": story_text,
                    "team_members": ", ".join(team_members),
                    "format_instructions": self.parser.get_format_instructions()
                })
                return result
            except Exception as e:
                if "429" in str(e) or "quota" in str(e).lower():
                    wait_time = 20 * (attempt + 1)
                    print(f"⏳ Rate limited during claim extraction. Waiting {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                raise e
        
        raise Exception("Failed to extract claims after multiple retries due to rate limits.")


# Test if run directly
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    from pathlib import Path
    
    load_dotenv()
    
    # Load your scraped data
    output_dir = Path('../output')
    test_file = output_dir / 'lavalock.json'
    
    if test_file.exists():
        with open(test_file, 'r', encoding='utf-8') as f:
            devpost_data = json.load(f)
        
        # Extract claims
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            print("❌ Set GOOGLE_API_KEY in .env file")
            exit(1)
        
        extractor = ClaimExtractor(api_key=api_key)
        print(f"🔍 Extracting claims from: {devpost_data['title']}\n")
        
        claims = extractor.extract_claims(devpost_data)
        
        print("✅ Extracted Claims:")
        print(json.dumps(claims.dict(), indent=2))
    else:
        print(f"❌ Test file not found: {test_file}")
        print("Run the Devpost scraper first to generate test data.")
