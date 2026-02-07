# HackID Backend Setup

## Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Then edit `.env` and add your API keys:

```env
OPENAI_API_KEY=sk-your-actual-openai-key
GITHUB_TOKEN=ghp_your-github-token-optional
```

> **Note:** GitHub token is optional but increases rate limits from 60 to 5000 requests/hour.

### 3. Test Agent 1 (Claim Extractor)

```bash
cd backend
python agents/claim_extractor.py
```

Expected output: Extracted claims from LavaLock project

### 4. Test Agent 2 (GitHub Validator)

```bash
python agents/github_validator.py
```

Expected output: Validation report with tech stack, team, and timeline checks

### 5. Test Full Pipeline

```bash
python pipeline.py
```

Expected output: Complete validation report saved to `validation_result.json`

---

## Project Structure

```
hackID/
├── backend/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── claim_extractor.py    # Agent 1: Extract claims from Devpost
│   │   └── github_validator.py   # Agent 2: Validate against GitHub
│   ├── pipeline.py                # Orchestrates both agents
│   └── requirements.txt
├── scraper.py                     # Devpost scraper (existing)
├── output/                        # Scraped project data (existing)
└── .env                           # API keys (create this)
```

---

## Next Steps

Once agents are working:

1. **Create FastAPI backend** (`backend/main.py`)
2. **Add database** (SQLite for demo)
3. **Build frontend** (Next.js)
4. **Deploy** (Railway/Vercel)

See `implementation_plan.md` for the full roadmap!
