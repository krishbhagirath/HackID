import os
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv(dotenv_path="../.env")
api_key = os.getenv("GOOGLE_API_KEY")

models = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]

for model_name in models:
    print(f"Testing {model_name}...")
    try:
        llm = ChatGoogleGenerativeAI(model=model_name, google_api_key=api_key)
        response = llm.invoke("Hi")
        print(f"✅ {model_name} worked!")
        # Save the winner
        with open("winner_model.txt", "w") as f:
            f.write(model_name)
        break
    except Exception as e:
        print(f"❌ {model_name} failed: {e}")
