# Configuration
# Edit this file to change your API keys and secrets
import os

# Google Gemini API Key - Use environment variable for security
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'your_gemini_api_key_here')

# Flask Secret Key - Use environment variable for security
FLASK_SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')

# Add other API keys here as needed
# OPENAI_API_KEY = "your_openai_key_here"

# ANTHROPIC_API_KEY = "your_anthropic_key_here"
