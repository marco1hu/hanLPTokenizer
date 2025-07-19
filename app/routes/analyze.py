from flask import Blueprint, request, jsonify, g, current_app as app
from ..services.auth import firebase_auth_required
from ..services.tokenizer import tokenize_text
from ..services.deepseek_client import chat_with_deepseek
from ..services.splitter import split_sentence
from ..utils.analyze_prompts import get_translation_messages
from ..services.gpt_client import chat_with_chatgpt



analyze_bp = Blueprint("analyze", __name__, url_prefix="/analyze")

@analyze_bp.route("", methods=["POST"])
@firebase_auth_required
def analyze():
    data = request.get_json()
    sentence = data.get("text", "").strip()
    lang = data.get("lang", "en")

    if not sentence:
        return jsonify({"error": "Empty input"}), 400

    try:
        chunks = split_sentence(sentence)

        all_tokens = []
        full_translation = ""
        position_counter = 0

        for chunk in chunks:
            tokens = tokenize_text(chunk)
            if not tokens:
                continue

            messages = get_translation_messages(lang=lang, sentence=chunk, tokens=tokens)


            if g.user.role == "premium":
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

            for idx, token in enumerate(tokens):
                all_tokens.append({
                    "position": position_counter,
                    "token": token,
                    "translation": token_translations.get(token, "")
                })
                position_counter += 1

            full_translation += chunk_translation + " "

        return jsonify({
            "full_translation": full_translation.strip(),
            "token_list": all_tokens
        })

    except Exception as e:
        app.logger.exception(f"Errore su /analyze: {str(e)}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500
