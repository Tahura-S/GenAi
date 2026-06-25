from dotenv import load_dotenv
from groq import Groq
import os

# Load .env
load_dotenv()

# Create Groq client
client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

#prompt
prompt = input("Enter your prompt: ")

# Send request
response = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    temperature=1.0,
    top_p=1.0,
    max_tokens=200,
    presence_penalty=2.0,
    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ]

    # messages=[
    # {
    #     "role": "system",
    #     "content": "You are teaching a 10-year-old child"
    # },
    # {
    #     "role": "user",
    #     "content": prompt
    # }
    # ]
)
print("\nGenerated Response:\n")
print(response.choices[0].message.content)
