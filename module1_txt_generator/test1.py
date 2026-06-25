#This was to check if the api key was loaded successfully or not
# from dotenv import load_dotenv
# import os

# load_dotenv()

# api_key = os.getenv("GEMINI_API_KEY")

# if api_key:
#     print("API Key loaded successfully!")
#     print(f"First 10 chars: {api_key[:10]}")
# else:
#     print("API Key not found!")

#actually implementation starts herefrom dotenv import load_dotenv
from dotenv import load_dotenv
from google import genai
import os
from google.genai import types

# Load .env file
load_dotenv()

# Create client
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)



# Generate response
prompt = input("Enter your prompt: ")

try:
    print("Sending request...")
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=1.5
        )
    )

    print("\nGenerated Response:\n")
    print(response.text)

except Exception as e:
    print("\nRequest failed.")
    print(type(e).__name__)
    print(e)