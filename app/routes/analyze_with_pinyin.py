from flask import Blueprint, request, jsonify, g, current_app as app
from ..services.auth import firebase_auth_required
from ..services.tokenizer import tokenize_text
from ..services.deepseek_client import chat_with_deepseek
from ..services.splitter import split_sentence
from pypinyin import lazy_pinyin, Style

analyze_with_pinyin_bp = Blueprint("analyze_with_pinyin", __name__, url_prefix="/analyze_with_pinyin")

@analyze_with_pinyin_bp.route("", methods=["POST"])
@firebase_auth_required
def analyze_with_pinyin():
    data = request.get_json()
    sentence = data.get("text", "").strip()
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

            messages = [
                {"role": "system", "content": "You are a precise Chinese-English translator. Return only plain text. No markdown, no commentary."},
                {"role": "user", "content": (
                    f"Sentence: {chunk}\n"
                    f"Tokens: {tokens}\n\n"
                    f"Your task:\n"
                    f"1. Translate the sentence into natural English.\n"
                    f"2. Then, write each token followed by a colon and its literal translation, one per line.\n\n"
                    f"Example format:\n"
                    f"Natural English translation here. (required)\n"
                    f"token1: translation1\n"
                    f"token2: translation2\n"
                    f"...\n"
                )}
            ]

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
                    "pinyin": ' '.join(lazy_pinyin(token, style=Style.TONE)),
                    "translation": token_translations.get(token, "")
                })
                position_counter += 1

            full_translation += chunk_translation + " "

        return jsonify({
            "full_translation": full_translation.strip(),
            "token_list": all_tokens
        })

    except Exception as e:
        app.logger.exception(f"Errore su /analyze_with_pinyin: {str(e)}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500
