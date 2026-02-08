# Quick Setup Script for HackID Backend
# Run this to get started fast!

Write-Host "🚀 Setting up HackID Backend..." -ForegroundColor Cyan

# Check if .env exists
if (!(Test-Path ".env")) {
    Write-Host "📝 Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "⚠️  IMPORTANT: Edit .env and add your GOOGLE_API_KEY!" -ForegroundColor Red
    Write-Host ""
} else {
    Write-Host "✅ .env file already exists" -ForegroundColor Green
}

# Install dependencies
Write-Host "📦 Installing Python dependencies..." -ForegroundColor Cyan
pip install -r requirements.txt

Write-Host ""
Write-Host "✅ Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Edit .env and add your GOOGLE_API_KEY"
Write-Host "2. Test Agent 1: `$env:PYTHONPATH='backend'; python backend/agents/claim_extractor.py`"
Write-Host "3. Test Agent 2: `$env:PYTHONPATH='backend'; python backend/agents/github_validator.py`"
Write-Host "4. Test Pipeline: `$env:PYTHONPATH='backend'; python backend/pipeline.py gallery <url>`"
Write-Host ""
