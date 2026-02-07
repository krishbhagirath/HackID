"""
Simple test to verify Gemini API is working after billing upgrade.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Test with the google-generativeai library directly
import google.generativeai as genai

api_key = os.getenv('GOOGLE_API_KEY')
if not api_key:
    print("❌ No GOOGLE_API_KEY found in .env")
    exit(1)

print(f"✓ API Key found: {api_key[:10]}...")

# Configure the API
genai.configure(api_key=api_key)

# Make a simple test call
try:
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    response = model.generate_content("Say 'Hello, world!' if you can hear me.")
    
    print("\n✅ SUCCESS! Gemini API is working!")
    print(f"Response: {response.text}")
    
except Exception as e:
    print(f"\n❌ FAILED: {e}")
