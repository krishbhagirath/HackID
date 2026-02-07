"""
List all available Gemini models for your API key.
"""
import os
from dotenv import load_dotenv
import requests

load_dotenv()

api_key = os.getenv('GOOGLE_API_KEY')
if not api_key:
    print("❌ No GOOGLE_API_KEY found in .env")
    exit(1)

print(f"✓ API Key found: {api_key[:10]}...\n")

# List models using the REST API directly
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"

try:
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        models = data.get('models', [])
        
        print(f"✅ Found {len(models)} available models:\n")
        
        for model in models:
            name = model.get('name', 'Unknown')
            display_name = model.get('displayName', 'Unknown')
            supported_methods = model.get('supportedGenerationMethods', [])
            
            # Only show models that support generateContent
            if 'generateContent' in supported_methods:
                print(f"  ✓ {name}")
                print(f"    Display: {display_name}")
                print(f"    Methods: {', '.join(supported_methods)}\n")
    else:
        print(f"❌ Failed to list models")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"❌ Error: {e}")
