from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

response = client.chat.completions.create(
    model="openrouter/auto",
    messages=[
        {"role": "user", "content": "Diz oi pra mim em português"}
    ]
)

print(response.choices[0].message.content)