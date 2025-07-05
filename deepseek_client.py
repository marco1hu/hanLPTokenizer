import os
from dotenv import load_dotenv
from flask import current_app as app  
import time
from openai import OpenAI
from openai._exceptions import APITimeoutError

load_dotenv()

# === DeepSeek Setup ===
deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_TIMEOUT = int(os.getenv("DEEPSEEK_TIMEOUT", 15)) 
fallback_enabled = os.getenv("FALLBACK_ENABLED", "false").lower() == "true"

def chat_with_deepseek(messages, model="deepseek-chat", temperature=0.7):
    deepseek_client = OpenAI(
        api_key=deepseek_api_key,
        base_url="https://api.deepseek.com/v1"
    )

    for attempt in range(2):  
        try:
            response = deepseek_client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                timeout=DEEPSEEK_TIMEOUT
            )
            return response.choices[0].message.content.strip()
        except APITimeoutError as e:
            app.logger.warning(f"Tentativo {attempt + 1} - DeepSeek timeout: {e}")
            time.sleep(1)
        except Exception as e:
            app.logger.warning(f"Tentativo {attempt + 1} - DeepSeek errore: {str(e)}")
            time.sleep(1)

    app.logger.warning("DeepSeek ha fallito dopo 2 tentativi.")

    if fallback_enabled:
        app.logger.info("Fallback attivo: passo a OpenAI GPT (gpt-3.5-turbo)")
        try:
            return chat_with_fallback(messages, model="gpt-3.5-turbo", temperature=temperature)
        except Exception as fallback_error:
            app.logger.exception("Errore anche nel fallback OpenAI")
            raise Exception("Both DeepSeek and fallback failed.")
    else:
        raise Exception("DeepSeek failed and fallback is disabled.")



def chat_with_fallback(messages, model="gpt-3.5-turbo", temperature=0.7):
    openai_client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url="https://api.openai.com/v1"
    )
    response = openai_client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature
    )
    return response.choices[0].message.content.strip()

def chat_with_chatgpt(messages, model="gpt-4o", temperature=0.5):
    openai_client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url="https://api.openai.com/v1"
    )

    try:
        app.logger.info("Chiamata a OpenAI GPT (uso per /explain)")
        response = openai_client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        app.logger.exception(f"Errore nella chiamata GPT per explain: {str(e)}")
        raise
