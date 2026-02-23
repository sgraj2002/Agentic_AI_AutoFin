import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# Load .env from the AGImpl folder
env_path = os.path.join(os.path.dirname(__file__), '..', 'AGImpl', '.env')
load_dotenv(env_path)

def test_openai():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY not found in .env file.")
        return

    print("Testing OpenAI API connectivity...")
    try:
        llm = ChatOpenAI(model="gpt-4o-mini", openai_api_key=api_key)
        response = llm.invoke("Hello, are you working correctly?")
        print("\nOpenAI Response:")
        print(response.content)
        print("\nSuccess: OpenAI API is connected and working!")
    except Exception as e:
        print(f"\nError connecting to OpenAI: {e}")

if __name__ == "__main__":
    test_openai()
