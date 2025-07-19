from flask import Blueprint, request, jsonify, g, current_app as app
from concurrent.futures import ThreadPoolExecutor, as_completed
from ..services.auth import firebase_auth_required
from ..services.tokenizer import tokenize_text
from ..services.deepseek_client import chat_with_deepseek
from ..services.gpt_client import chat_with_chatgpt
from ..services.splitter import split_sentence
from pypinyin import lazy_pinyin, Style
from ..utils.analyze_prompts import get_translation_messages

analyze_with_pinyin_bp = Blueprint("analyze_with_pinyin", __name__, url_prefix="/analyze_with_pinyin")

@analyze_with_pinyin_bp.route("", methods=["POST"])
@firebase_auth_required
def analyze_with_pinyin():
    data = request.get_json()
    sentence = data.get("text", "").strip()
    lang = data.get("lang", "en")
    
    if not sentence:
        return jsonify({"error": "Empty input"}), 400

    try:
        chunks = split_sentence(sentence)
        user_role = g.user.role

        
        tokenized_chunks = [(i, chunk, tokenize_text(chunk)) for i, chunk in enumerate(chunks) if tokenize_text(chunk)]


        # Parallelizza l'elaborazione GPT/DeepSeek
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [
                executor.submit(process_chunk, i, chunk, tokens, user_role, lang)
                for i, chunk, tokens in tokenized_chunks
            ]
            results = [f.result() for f in as_completed(futures)]
            results.sort(key=lambda r: r["index"]) 


        # Ricostruzione ordinata
        all_tokens = []
        position_counter = 0
        full_translation = ""

        for result in results:
            for token in result["token_items"]:
                token["position"] = position_counter
                all_tokens.append(token)
                position_counter += 1
            full_translation += result["chunk_translation"] + " "


        return jsonify({
            "full_translation": full_translation.strip(),
            "token_list": all_tokens
        })

    except Exception as e:
        app.logger.exception(f"Errore su /analyze_with_pinyin: {str(e)}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500
    
    

def process_chunk(index, chunk, tokens, role, lang):

    messages = get_translation_messages(lang=lang, sentence=chunk, tokens=tokens)

    if role == "premium":
        response_text = chat_with_chatgpt(messages, model="gpt-4o", temperature=0.7).strip()
    else:
        response_text = chat_with_deepseek(messages).strip()

    lines = response_text.splitlines()
    chunk_translation = ""
    token_translations = {}

    for line in lines:
        if not chunk_translation and ':' not in line and len(line.strip()) > 10:
            chunk_translation = line.strip()
        elif ':' in line:
            parts = line.split(':', 1)
            token_translations[parts[0].strip()] = parts[1].strip()

    token_items = []
    for token in tokens:
        token_items.append({
            "token": token,
            "pinyin": ' '.join(lazy_pinyin(token, style=Style.TONE)),
            "translation": token_translations.get(token, "")
        })

    return {
        "index": index,
        "token_items": token_items,
        "chunk_translation": chunk_translation
    }
