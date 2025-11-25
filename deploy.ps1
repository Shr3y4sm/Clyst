# Quick deployment script for Clyst (Windows)

Write-Host "🚀 Clyst Deployment Helper" -ForegroundColor Cyan
Write-Host "==========================" -ForegroundColor Cyan
Write-Host ""

# Check if git is initialized
if (-not (Test-Path ".git")) {
    Write-Host "❌ Git not initialized. Initializing..." -ForegroundColor Yellow
    git init
    git add .
    git commit -m "Initial commit"
    Write-Host "✅ Git initialized" -ForegroundColor Green
}

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  .env file not found!" -ForegroundColor Yellow
    Write-Host "📝 Copy .env.example to .env and fill in your API keys:" -ForegroundColor Yellow
    Write-Host "   Copy-Item .env.example .env" -ForegroundColor White
    Write-Host ""
    exit 1
}

Write-Host "✅ Environment file found" -ForegroundColor Green

# Check if virtual environment is activated
if ($null -eq $env:VIRTUAL_ENV) {
    Write-Host "⚠️  Virtual environment not activated!" -ForegroundColor Yellow
    Write-Host "Run: .\.venv\Scripts\Activate.ps1" -ForegroundColor White
    Write-Host ""
    exit 1
}

Write-Host "✅ Virtual environment active" -ForegroundColor Green

# Check requirements
Write-Host ""
Write-Host "📦 Checking dependencies..." -ForegroundColor Cyan
pip install -r requirements.txt --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Dependencies OK" -ForegroundColor Green
}

# Test database
Write-Host ""
Write-Host "🗄️  Testing database..." -ForegroundColor Cyan
python -c "from app import app, db; app.app_context().push(); db.create_all(); print('✅ Database OK')"

# Test imports
Write-Host ""
Write-Host "📚 Testing imports..." -ForegroundColor Cyan
python -c "import app; print('✅ App imports OK')"

Write-Host ""
Write-Host "✅ All checks passed!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next steps for deployment:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1️⃣  RENDER.COM (Recommended - Easiest):" -ForegroundColor Yellow
Write-Host "   - Visit: https://render.com" -ForegroundColor White
Write-Host "   - Sign in with GitHub" -ForegroundColor White
Write-Host "   - New Web Service → Connect repository" -ForegroundColor White
Write-Host "   - Set environment variables (GEMINI_API_KEY, GROQ_API_KEY)" -ForegroundColor White
Write-Host "   - Deploy!" -ForegroundColor White
Write-Host ""
Write-Host "2️⃣  RAILWAY.APP:" -ForegroundColor Yellow
Write-Host "   - Visit: https://railway.app" -ForegroundColor White
Write-Host "   - New Project → Deploy from GitHub" -ForegroundColor White
Write-Host "   - Add PostgreSQL database" -ForegroundColor White
Write-Host "   - Set environment variables" -ForegroundColor White
Write-Host "   - Deploy!" -ForegroundColor White
Write-Host ""
Write-Host "3️⃣  Test locally with production server:" -ForegroundColor Yellow
Write-Host "   gunicorn --bind 127.0.0.1:5000 app:app" -ForegroundColor White
Write-Host ""
Write-Host "📖 Full guide: See DEPLOYMENT.md" -ForegroundColor Cyan
Write-Host ""
