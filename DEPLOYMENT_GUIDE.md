# 🚀 Clyst Art Marketplace - Free Deployment Guide

This guide provides multiple free deployment options for your Clyst art marketplace application with all features working.

## 🔒 Security Setup (REQUIRED FIRST)

### 1. Environment Variables Setup
Create a `.env` file in your project root (this file is already in .gitignore):

```bash
# .env file
GEMINI_API_KEY=your_actual_gemini_api_key_here
FLASK_SECRET_KEY=your_secure_secret_key_here
FLASK_ENV=production
```

### 2. Generate Secure Secret Key
```python
import secrets
print(secrets.token_hex(32))
```

## 🌐 Free Deployment using Railway:

**Steps:**
1. Push your code to GitHub
2. Go to [Railway.app](https://railway.app)
3. Sign up with GitHub
4. Click "New Project" → "Deploy from GitHub repo"
5. Select your repository
6. Add environment variables in Railway dashboard:
   - `GEMINI_API_KEY`: Your Google Gemini API key
   - `FLASK_SECRET_KEY`: Your secure secret key
   - `FLASK_ENV`: production
7. Railway will automatically deploy your app

**Railway Configuration:**
- Your app will be available at: `https://your-app-name.railway.app`
- Database: SQLite (included)
- File storage: Local filesystem (included)
