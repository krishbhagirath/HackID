import os
from pathlib import Path
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

# Load .env from parent directory
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)
api_key = os.getenv("GOOGLE_API_KEY")

print("Testing LangChain with gemini-2.5-flash...")
try:
    # Trying the most standard configuration now that we know the model name is correct
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        api_key=api_key
    )
    response = llm.invoke("Hi")
    print(f"✅ gemini-2.5-flash worked with LangChain!")
    print(f"Response: {response.content}")
except Exception as e:
    import traceback
    print(f"❌ gemini-2.5-flash failed with LangChain: {e}")
    traceback.print_exc()
