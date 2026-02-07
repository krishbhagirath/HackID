import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv(dotenv_path="../.env")
api_key = os.getenv("GOOGLE_API_KEY")

print("Testing direct genai with gemini-2.5-flash...")

for version in ['v1', 'v1beta']:
    print(f"\n--- Testing API Version: {version} ---")
    try:
        genai.configure(api_key=api_key, transport='rest')
        # Note: genai.list_models() usually handles the version internally, 
        # but let's try to instantiate 
        model = genai.GenerativeModel('gemini-2.5-flash')
        # We can't easily force the version in GenerativeModel constructor in the same way,
        # but let's see if generate_content works.
        response = model.generate_content("Hi")
        print(f"✅ gemini-2.5-flash worked with {version}?")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Failed with {version}: {e}")
