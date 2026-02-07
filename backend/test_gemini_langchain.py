"""
Simple test using LangChain to verify Gemini API works after billing upgrade.
"""
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

api_key = os.getenv('GOOGLE_API_KEY')
if not api_key:
    print("❌ No GOOGLE_API_KEY found in .env")
    exit(1)

print(f"✓ API Key found: {api_key[:10]}...")

try:
    # Use the correct model name from the API
    llm = ChatGoogleGenerativeAI(
        model="models/gemini-2.5-flash",
        temperature=0,
        google_api_key=api_key,
        transport="rest"
    )
    
    print("\n🔄 Making test API call...")
    response = llm.invoke("Say 'Hello!' if you can hear me.")
    
    print("\n✅ SUCCESS! Gemini API is working!")
    print(f"Response: {response.content}")
    
except Exception as e:
    print(f"\n❌ FAILED!")
    print(f"Error type: {type(e).__name__}")
    print(f"Error message: {str(e)}")
    
    if "429" in str(e):
        print("\n⚠️  Still rate limited. The billing upgrade may need a few minutes to propagate.")
    elif "quota" in str(e).lower():
        print("\n⚠️  Quota issue. Check Google Cloud Console billing status.")
    else:
        print("\n⚠️  Unknown error. Check your API key and billing settings.")
