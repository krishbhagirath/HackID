"""Simple Gemini API test - no special characters"""
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()
api_key = os.getenv('GOOGLE_API_KEY')

print("Testing Gemini API...")
print(f"API Key: {api_key[:10]}...")

try:
    llm = ChatGoogleGenerativeAI(
        model="models/gemini-2.5-flash",
        temperature=0,
        google_api_key=api_key,
        transport="rest"
    )
    
    print("Making API call...")
    response = llm.invoke("Say hello in one word.")
    
    print("\nSUCCESS!")
    print(f"Response: {response.content}")
    
except Exception as e:
    print(f"\nFAILED: {type(e).__name__}")
    print(f"Message: {str(e)[:200]}")
