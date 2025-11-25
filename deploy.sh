#!/bin/bash
# Quick deployment script for Clyst

echo "🚀 Clyst Deployment Helper"
echo "=========================="
echo ""

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "❌ Git not initialized. Initializing..."
    git init
    git add .
    git commit -m "Initial commit"
    echo "✅ Git initialized"
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found!"
    echo "📝 Copy .env.example to .env and fill in your API keys:"
    echo "   cp .env.example .env"
    echo ""
    exit 1
fi

echo "✅ Environment file found"

# Check requirements
echo ""
echo "📦 Checking dependencies..."
pip install -r requirements.txt --quiet

# Test database
echo ""
echo "🗄️  Testing database..."
python -c "from app import app, db; app.app_context().push(); db.create_all(); print('✅ Database OK')"

# Test imports
echo ""
echo "📚 Testing imports..."
python -c "import app; print('✅ App imports OK')"

echo ""
echo "✅ All checks passed!"
echo ""
echo "📋 Next steps for deployment:"
echo ""
echo "1️⃣  RENDER.COM (Recommended - Easiest):"
echo "   - Visit: https://render.com"
echo "   - Sign in with GitHub"
echo "   - New Web Service → Connect repository"
echo "   - Set environment variables (GEMINI_API_KEY, GROQ_API_KEY)"
echo "   - Deploy!"
echo ""
echo "2️⃣  RAILWAY.APP:"
echo "   - Visit: https://railway.app"
echo "   - New Project → Deploy from GitHub"
echo "   - Add PostgreSQL database"
echo "   - Set environment variables"
echo "   - Deploy!"
echo ""
echo "3️⃣  FLY.IO (requires CLI):"
echo "   flyctl launch"
echo "   flyctl postgres create"
echo "   flyctl secrets set GEMINI_API_KEY=xxx"
echo "   flyctl deploy"
echo ""
echo "📖 Full guide: See DEPLOYMENT.md"
echo ""
