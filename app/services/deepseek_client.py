import os
import time
from dotenv import load_dotenv
from flask import current_app as app
from openai import OpenAI
from openai._exceptions import APITimeoutError
from .gpt_client import chat_with_fallback  # fallback GPT client

load_dotenv()

deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_TIMEOUT = int(os.getenv("DEEPSEEK_TIMEOUT", 15))
fallback_enabled = os.getenv("FALLBACK_ENABLED", "false").lower() == "true"


def chat_with_deepseek(messages, model="deepseek-chat", temperature=0.7, max_tokens=512):
    deepseek_client = OpenAI(
        api_key=deepseek_api_key,
        base_url="https://api.deepseek.com/v1"
    )

    start = time.perf_counter()
    try:
        response = deepseek_client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            timeout=DEEPSEEK_TIMEOUT,
            max_tokens=max_tokens
        )
        duration = time.perf_counter() - start
        app.logger.info(f"DeepSeek completato in {duration:.2f}s")
        return response.choices[0].message.content.strip()

    except APITimeoutError as e:
        app.logger.warning(f"Timeout DeepSeek: {e}")
    except Exception as e:
        app.logger.warning(f"Errore DeepSeek: {str(e)}")

    if fallback_enabled:
        app.logger.info("Fallback attivo → uso OpenAI GPT (gpt-3.5-turbo)")
        try:
            return chat_with_fallback(messages, model="gpt-3.5-turbo", temperature=temperature)
        except Exception as fallback_error:
            app.logger.exception("Errore anche nel fallback OpenAI")
            raise Exception("Both DeepSeek and fallback failed.")
    else:
        raise Exception("DeepSeek failed and fallback is disabled.")
