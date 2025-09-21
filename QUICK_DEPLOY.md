# 🚀 Quick Deploy Guide - Clyst Art Marketplace

## ⚡ 5-Minute Deployment

### Step 1: Prepare Your Code
```bash
# Run the deployment preparation script
python deploy.py

# Edit .env file and add your Google Gemini API key
# Replace 'your_gemini_api_key_here' with your actual key
```

### Step 2: Push to GitHub
```bash
git add .
git commit -m "Prepare for deployment"
git push origin main
```

### Step 3: Deploy on Railway (Recommended)
1. Go to [Railway.app](https://railway.app)
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your Clyst repository
5. Add environment variables in Railway dashboard:
   - `GEMINI_API_KEY`: Your Google Gemini API key
   - `FLASK_SECRET_KEY`: Your secure secret key (from .env file)
   - `FLASK_ENV`: production
6. Railway will automatically deploy your app

### Step 4: Access Your App
Your app will be live at: `https://your-app-name.railway.app`

## 🎯 What You Get

✅ **Fully Functional Art Marketplace**
- User registration and authentication
- AI-powered content generation
- Natural language search
- Multilingual support (15+ languages)
- File uploads for artwork
- Community feed and marketplace

✅ **All AI Features Working**
- Google Gemini integration
- Automatic title/description generation
- Image analysis
- Portfolio narratives
- Translation support

✅ **Production Ready**
- Secure environment variables
- Database configuration
- File storage
- Error handling

## 🔧 Alternative Hosting Options

### Render (Free Tier)
- 750 hours/month free
- PostgreSQL database
- Custom domains

### Fly.io (Free Tier)
- 3 shared-cpu VMs
- Global deployment
- Built-in database

### PythonAnywhere (Free Tier)
- 1 web app
- Easy setup
- Built-in file storage

## 🆘 Need Help?

1. Check `DEPLOYMENT_GUIDE.md` for detailed instructions
2. Verify your Google Gemini API key is valid
3. Make sure all environment variables are set
4. Check deployment logs for errors

---

**Your Clyst art marketplace will be live with all features working!** 🎨✨
