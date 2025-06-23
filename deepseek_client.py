import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("DEEPSEEK_API_KEY")

# Usa client OpenAI ma con endpoint DeepSeek
client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com/v1"
)

def chat_with_deepseek(messages, model="deepseek-chat", temperature=0.7):

    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"[Errore DeepSeek] {str(e)}"
