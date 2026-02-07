import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv(dotenv_path="../.env")
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

print(f"API Key: {api_key[:5]}...{api_key[-5:]}")
try:
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content("Hi")
    print("✅ Success with gemini-1.5-flash via direct genai")
    print(response.text)
except Exception as e:
    print(f"❌ Error with gemini-1.5-flash via direct genai: {e}")
