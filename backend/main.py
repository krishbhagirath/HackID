from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import os
from dotenv import load_dotenv

# Import the existing pipeline
from backend.pipeline import ValidationPipeline
from backend.database import init_db

load_dotenv()

app = FastAPI(title="HackID Validation API")

# Initialize database tables on startup
@app.on_event("startup")
def startup_event():
    init_db()

# VERY IMPORTANT: Configure CORS for your Next.js frontend
# In production, replace ["*"] with your actual frontend URL (e.g. https://hackid.vercel.app)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the pipeline once
google_api_key = os.getenv("GOOGLE_API_KEY")
github_token = os.getenv("GITHUB_TOKEN")

if not google_api_key:
    raise ValueError("GOOGLE_API_KEY must be set in environment variables")

pipeline = ValidationPipeline(google_api_key=google_api_key, github_token=github_token)

class ValidationRequest(BaseModel):
    devpost_url: str
    hackathon_url: str

class BatchValidationRequest(BaseModel):
    hackathon_url: str
    max_projects: Optional[int] = 10

@app.get("/")
async def root():
    return {"status": "ok", "message": "HackID API is running"}

@app.post("/validate")
async def validate_project(request: ValidationRequest):
    """
    Endpoint to validate a single project from Devpost and GitHub.
    Automatically saves results to Supabase.
    """
    try:
        result = pipeline.validate_from_url(
            devpost_url=request.devpost_url,
            hackathon_url=request.hackathon_url
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/validate-batch")
async def validate_batch(request: BatchValidationRequest):
    """
    Scrape a hackathon gallery and validate multiple projects.
    Automatically saves results to Supabase.
    """
    try:
        results = pipeline.validate_hackathon(
            hackathon_url=request.hackathon_url,
            max_projects=request.max_projects,
            delay_seconds=2.0 
        )
        return {
            "hackathon_url": request.hackathon_url,
            "projects_processed": len(results),
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # Render provides PORT in environment
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
