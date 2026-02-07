# hackID - AI-Powered Hackathon Verification System

An autonomous multi-agent system that verifies hackathon submissions by analyzing Devpost projects and GitHub repositories to detect discrepancies and validate eligibility.

## 🎯 Project Vision

Hackathon organizers receive hundreds of submissions. Manually reviewing each project's code, commit history, and claimed features is time-consuming and error-prone. **hackID** automates this process using AI agents to:

1. ✅ Extract claims from Devpost submissions
2. ✅ Analyze GitHub repositories
3. ✅ Compare claimed features vs actual code
4. ✅ Validate commit timings for eligibility
5. ✅ Flag suspicious projects for manual review

## 🏗️ System Architecture

```mermaid
graph TD
    A[CSV Upload] --> B[Orchestrator Agent]
    B --> C[Devpost Scraper]
    C --> D[Claim Extractor AI]
    D --> E[GitHub Analyzer AI]
    E --> F[Comparison AI]
    F --> G[Eligibility Checker]
    G --> H[Flagging Decision]
    H --> I[Report Generation]
```

### Agent Roles

| Agent | Responsibility |
|-------|----------------|
| **Orchestrator** | Coordinates workflow and agent communication |
| **Devpost Scraper** | Extracts project data from Devpost pages |
| **Claim Extractor** | Uses LLM to identify technical claims and features |
| **GitHub Analyzer** | Analyzes code, tech stack, and commit history |
| **Comparison Agent** | Validates claims against actual code |
| **Eligibility Checker** | Verifies commits are within hackathon dates |
| **Flagging Decision** | Determines if manual review is needed |

## 🚀 Current Status: Phase 1 - Prototype

The prototype demonstrates Devpost scraping capabilities on real hackathon projects.

### What Works Now

✅ **Devpost Scraper** - Extracts comprehensive project data:
- Project title and tagline
- Full story sections (Inspiration, What it does, How we built it, Challenges, etc.)
- Tech stack ("Built With" tags)
- GitHub repository links
- Team member information
- External links and prizes

### Example Output

```json
{
  "title": "deltawash",
  "story": {
    "Inspiration": "One time my dentist handled the tools...",
    "What it does": "Our product checks that the complete WHO protocol...",
    "How we built it": "On the hardware side, a Pi cam is used..."
  },
  "built_with": ["python", "pytorch", "tensorflow", "react", "raspberry-pi"],
  "github_repo": "https://github.com/Goldenstar2660/DeltaWash"
}
```

## 📦 Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd hackID

# Install dependencies
pip install requests beautifulsoup4 lxml

# For full multi-agent system (Phase 2+):
pip install langchain langchain-openai python-dotenv
```

## 🧪 Testing the Scraper

```bash
python test_scraper.py
```

This will scrape the DeltaHacks 12 project "deltawash" and save the output to `output/deltawash.json`.

### Testing with More Projects

Edit `test_scraper.py` and add more Devpost URLs:

```python
test_projects = [
    'https://devpost.com/software/deltawash',
    'https://devpost.com/software/your-project-url',
    # Add more...
]
```

## 🗺️ Roadmap

### ✅ Phase 1: Prototype (COMPLETE)
- [x] Devpost scraper
- [x] Data extraction
- [x] JSON output

### 🔄 Phase 2: Multi-Agent System (NEXT)
- [ ] LangChain integration
- [ ] Claim extraction agent (LLM-powered)
- [ ] GitHub API integration
- [ ] Code analysis agent
- [ ] Comparison logic
- [ ] Eligibility checker

### 📋 Phase 3: CSV Processing
- [ ] Batch processing from CSV
- [ ] Progress tracking
- [ ] Error handling
- [ ] Report generation

### 🌐 Phase 4: Web Interface
- [ ] Flask/FastAPI backend
- [ ] Upload CSV interface
- [ ] Real-time progress display
- [ ] Download flagging report

## 🔧 Technical Details

### How Devpost Scraping Works

The scraper uses BeautifulSoup to parse HTML and extract:

1. **Title**: From `<h1 id="app-title">`
2. **Story Sections**: Parses `<h2>` headers and associated `<p>` tags
3. **Tech Stack**: Extracts `<span class="cp-tag">` elements
4. **GitHub Link**: Searches for links containing "github.com"
5. **Team**: Parses `<div id="app-team">` section

### Why This Approach?

- **No API required**: Devpost doesn't have a public API
- **Robust**: Uses multiple selectors to handle different page layouts
- **Structured data**: Organizes story into sections for easier AI analysis
- **Complete**: Captures all metadata needed for verification

## 🤖 How AI Agents Will Work (Phase 2)

### Claim Extraction
```python
# Example: LLM extracts structured claims
claims = {
    "technologies": ["TensorFlow", "React", "Raspberry Pi"],
    "features": [
        "Computer vision for hand washing detection",
        "Real-time LED feedback",
        "Web dashboard for compliance tracking"
    ],
    "complexity_claims": ["First time using Raspberry Pi"]
}
```

### GitHub Analysis
```python
# Agent analyzes actual code
analysis = {
    "detected_languages": ["Python", "JavaScript", "C++"],
    "frameworks_used": ["TensorFlow", "React"],
    "commit_timeline": [...],
    "lines_of_code": 2500
}
```

### Comparison
```python
# Agent compares claims vs reality
verification = {
    "tech_match": True,  # TensorFlow, React confirmed
    "features_validated": ["Computer vision present", "React dashboard exists"],
    "red_flags": ["80% of code committed before hackathon start"]
}
```

## 📊 Expected Workflow

1. **Upload CSV**: `participant_name, devpost_url, hackathon_dates`
2. **Scrape**: Extract all project data
3. **Extract Claims**: LLM identifies what team claims they built
4. **Analyze GitHub**: Get actual code and commit history
5. **Compare**: Validate claims against reality
6. **Check Eligibility**: Ensure commits are within hackathon timeframe
7. **Flag**: Output projects needing manual review

## 🤝 Contributing

This is currently a prototype. Contributions welcome for:
- Additional Devpost parsing edge cases
- GitHub API integration
- LangChain multi-agent implementation
- Testing with more hackathons

## 📄 License

MIT License - Feel free to use for your hackathon!

## 🙏 Acknowledgments

Built with inspiration from real hackathon challenges. Tested on DeltaHacks 12 projects.
