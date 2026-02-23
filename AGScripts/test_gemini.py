import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# Load .env from the AGImpl folder
env_path = os.path.join(os.path.dirname(__file__), '..', 'AGImpl', '.env')
load_dotenv(env_path)

def test_gemini():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not found in .env file.")
        return

    print("Listing available Gemini models...")
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"- {m.name}")
        
        print("\nAttempting to connect with models/gemini-flash-latest...")
        llm = ChatGoogleGenerativeAI(model="gemini-flash-latest", google_api_key=api_key)
        response = llm.invoke("Hello, are you working correctly?")
        print("\nGemini Response:")
        print(response.content)
        print("\nSuccess: Gemini API is connected and working!")
    except Exception as e:
        print(f"\nError connecting to Gemini: {e}")

if __name__ == "__main__":
    test_gemini()
