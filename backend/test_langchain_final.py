import os
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv(dotenv_path="../.env")
api_key = os.getenv("GOOGLE_API_KEY")

print("Testing LangChain with gemini-2.5-flash and transport='rest'...")
try:
    # Trying the most standard configuration now that we know the model name is correct
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=api_key,
        transport="rest"
    )
    response = llm.invoke("Hi")
    print(f"✅ gemini-2.5-flash worked with LangChain!")
    print(f"Response: {response.content}")
except Exception as e:
    print(f"❌ gemini-2.5-flash failed with LangChain: {e}")
