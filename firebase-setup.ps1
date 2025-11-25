# Firebase Setup Guide for Clyst Deployment

Write-Host "🔥 Firebase Configuration Helper" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "📋 Step 1: Create Firebase Project" -ForegroundColor Yellow
Write-Host "   1. Visit: https://console.firebase.google.com" -ForegroundColor White
Write-Host "   2. Click 'Add project' or select existing" -ForegroundColor White
Write-Host "   3. Name it: Clyst (or your preferred name)" -ForegroundColor White
Write-Host "   4. Enable Google Analytics (optional)" -ForegroundColor White
Write-Host ""

Write-Host "📋 Step 2: Enable Authentication" -ForegroundColor Yellow
Write-Host "   1. In Firebase Console, go to 'Authentication'" -ForegroundColor White
Write-Host "   2. Click 'Get Started'" -ForegroundColor White
Write-Host "   3. Enable sign-in methods:" -ForegroundColor White
Write-Host "      - Email/Password ✅" -ForegroundColor Green
Write-Host "      - Phone ✅ (for OTP verification)" -ForegroundColor Green
Write-Host "      - Google (optional)" -ForegroundColor Gray
Write-Host ""

Write-Host "📋 Step 3: Get Web App Config" -ForegroundColor Yellow
Write-Host "   1. Click ⚙️ Settings → Project Settings" -ForegroundColor White
Write-Host "   2. Scroll to 'Your apps' section" -ForegroundColor White
Write-Host "   3. Click '</>' (Web app) to add web app" -ForegroundColor White
Write-Host "   4. Name it: Clyst Web" -ForegroundColor White
Write-Host "   5. Copy the config object" -ForegroundColor White
Write-Host ""

Write-Host "📋 Step 4: Copy These Values to Render/Railway" -ForegroundColor Yellow
Write-Host "   You'll need these environment variables:" -ForegroundColor White
Write-Host ""
Write-Host "   FIREBASE_API_KEY=<from config.apiKey>" -ForegroundColor Cyan
Write-Host "   FIREBASE_AUTH_DOMAIN=<from config.authDomain>" -ForegroundColor Cyan
Write-Host "   FIREBASE_PROJECT_ID=<from config.projectId>" -ForegroundColor Cyan
Write-Host "   FIREBASE_STORAGE_BUCKET=<from config.storageBucket>" -ForegroundColor Cyan
Write-Host "   FIREBASE_MESSAGING_SENDER_ID=<from config.messagingSenderId>" -ForegroundColor Cyan
Write-Host "   FIREBASE_APP_ID=<from config.appId>" -ForegroundColor Cyan
Write-Host ""

Write-Host "📋 Step 5: Update Local .env (for testing)" -ForegroundColor Yellow
$envFile = ".env"

if (Test-Path $envFile) {
    Write-Host "   ✅ .env file exists" -ForegroundColor Green
    Write-Host "   Add your Firebase config values to .env:" -ForegroundColor White
    Write-Host ""
    Write-Host "   FIREBASE_API_KEY=AIzaSy..." -ForegroundColor Gray
    Write-Host "   FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com" -ForegroundColor Gray
    Write-Host "   FIREBASE_PROJECT_ID=your-project-id" -ForegroundColor Gray
    Write-Host "   FIREBASE_STORAGE_BUCKET=your-project.appspot.com" -ForegroundColor Gray
    Write-Host "   FIREBASE_MESSAGING_SENDER_ID=123456789" -ForegroundColor Gray
    Write-Host "   FIREBASE_APP_ID=1:123456789:web:abcdef" -ForegroundColor Gray
}
else {
    Write-Host "   ⚠️  .env file not found" -ForegroundColor Yellow
    Write-Host "   Create .env from .env.example first" -ForegroundColor White
}

Write-Host ""
Write-Host "✨ Optional: Service Account for Admin SDK" -ForegroundColor Yellow
Write-Host "   (Not required for college project, REST API works fine)" -ForegroundColor Gray
Write-Host "   1. Project Settings → Service Accounts" -ForegroundColor White
Write-Host "   2. Generate new private key" -ForegroundColor White
Write-Host "   3. Download JSON file" -ForegroundColor White
Write-Host "   4. For local: Save as firebase-key.json in project root" -ForegroundColor White
Write-Host "   5. For Render: Base64 encode and set as env var" -ForegroundColor White
Write-Host ""

Write-Host "🎯 For Deployment:" -ForegroundColor Cyan
Write-Host "   Just add the 6 FIREBASE_* environment variables to Render/Railway" -ForegroundColor White
Write-Host "   The app will automatically use REST API for authentication" -ForegroundColor White
Write-Host "   No service account needed!" -ForegroundColor Green
Write-Host ""

Write-Host "🧪 Test Firebase Locally:" -ForegroundColor Cyan
Write-Host "   1. Add Firebase values to .env" -ForegroundColor White
Write-Host "   2. Run: python app.py" -ForegroundColor White
Write-Host "   3. Visit: http://127.0.0.1:5000" -ForegroundColor White
Write-Host "   4. Try registering a new user" -ForegroundColor White
Write-Host "   5. Check Firebase Console → Authentication → Users" -ForegroundColor White
Write-Host ""

Write-Host "Done! Your Firebase is ready for deployment" -ForegroundColor Green
