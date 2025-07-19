import os
import time
import logging
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
logger = logging.getLogger(__name__)  # logger thread-safe

def chat_with_fallback(messages, model="gpt-3.5-turbo", temperature=0.6):
    openai_client = OpenAI(
        api_key=openai_api_key,
        base_url="https://api.openai.com/v1"
    )

    start = time.perf_counter()
    try:
        response = openai_client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature
        )
        duration = time.perf_counter() - start
        logger.info(f"OpenAI fallback ({model}) completato in {duration:.2f}s")
        return response.choices[0].message.content.strip()

    except Exception as e:
        duration = time.perf_counter() - start
        logger.exception(f"Errore durante fallback OpenAI ({model}) dopo {duration:.2f}s: {str(e)}")
        raise


def chat_with_chatgpt(messages, model="gpt-3.5-turbo", temperature=0.6):
    openai_client = OpenAI(
        api_key=openai_api_key,
        base_url="https://api.openai.com/v1"
    )

    start = time.perf_counter()
    try:
        logger.info(f"Chiamata a OpenAI GPT ({model}) in corso...")
        response = openai_client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature
        )
        duration = time.perf_counter() - start
        logger.info(f"OpenAI GPT completato in {duration:.2f}s")
        return response.choices[0].message.content.strip()

    except Exception as e:
        duration = time.perf_counter() - start
        logger.exception(f"Errore OpenAI GPT ({model}) dopo {duration:.2f}s: {str(e)}")
        raise
