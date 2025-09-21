#!/usr/bin/env python3
"""
Quick deployment script for Clyst Art Marketplace
This script helps you prepare your app for deployment
"""

import os
import secrets
import subprocess
import sys

def generate_secret_key():
    """Generate a secure secret key"""
    return secrets.token_hex(32)

def check_requirements():
    """Check if all required files exist"""
    required_files = [
        'app.py',
        'config.py', 
        'requirements.txt',
        'DEPLOYMENT_GUIDE.md'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        return False
    
    print("✅ All required files present")
    return True

def create_env_file():
    """Create .env file with secure values"""
    if os.path.exists('.env'):
        print("⚠️  .env file already exists. Skipping creation.")
        return
    
    secret_key = generate_secret_key()
    
    env_content = f"""# Environment Variables for Clyst Art Marketplace
# IMPORTANT: Replace 'your_gemini_api_key_here' with your actual Google Gemini API key

# Google Gemini API Key (Required for AI features)
# Get your key from: https://makersuite.google.com/app/apikey
GEMINI_API_KEY=your_gemini_api_key_here

# Flask Secret Key (Generated securely)
FLASK_SECRET_KEY={secret_key}

# Environment
FLASK_ENV=production

# Database URL (automatically set by hosting platforms)
# DATABASE_URL=postgresql://user:password@host:port/database

# Port (automatically set by hosting platforms)
# PORT=5000
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Created .env file with secure secret key")
    print("⚠️  IMPORTANT: Edit .env file and add your actual GEMINI_API_KEY")

def check_git_status():
    """Check git status and provide deployment instructions"""
    try:
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            if result.stdout.strip():
                print("📝 You have uncommitted changes:")
                print(result.stdout)
                print("💡 Consider committing changes before deployment:")
                print("   git add .")
                print("   git commit -m 'Prepare for deployment'")
                print("   git push origin main")
            else:
                print("✅ Git working directory is clean")
        else:
            print("⚠️  Git not initialized. Consider running:")
            print("   git init")
            print("   git add .")
            print("   git commit -m 'Initial commit'")
            
    except FileNotFoundError:
        print("⚠️  Git not found. Make sure Git is installed.")

def main():
    print("🚀 Clyst Art Marketplace - Deployment Preparation")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Create .env file
    create_env_file()
    
    # Check git status
    check_git_status()
    
    print("\n🎯 Next Steps:")
    print("1. Edit .env file and add your GEMINI_API_KEY")
    print("2. Push your code to GitHub")
    print("3. Follow the DEPLOYMENT_GUIDE.md for hosting options")
    print("\n💡 Recommended: Deploy on Railway.app (easiest setup)")
    print("   - Go to https://railway.app")
    print("   - Sign up with GitHub")
    print("   - Deploy from your repository")
    print("   - Add environment variables in Railway dashboard")
    
    print("\n✨ Your Clyst art marketplace is ready for deployment!")

if __name__ == "__main__":
    main()
