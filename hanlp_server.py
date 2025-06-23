from flask import Flask, request, jsonify
import hanlp
from pypinyin import lazy_pinyin, Style
import os
from dotenv import load_dotenv
from deepseek_client import chat_with_deepseek

app = Flask(__name__)
tokenizer = hanlp.load('PKU_NAME_MERGED_SIX_MONTHS_CONVSEG')
load_dotenv()
API_KEY = os.getenv("HANLP_API_KEY")
DK_API_KEY = os.getenv("DEEPSEEK_API_KEY")


@app.before_request
def auth():
    token = request.headers.get("Authorization", "")
    if token != f"Bearer {API_KEY}":
        return jsonify({"error": "Unauthorized"}), 401

@app.route('/tokenize', methods=['POST'])
def tokenize():
    data = request.get_json()
    sentence = data.get('text', '')
    tokens = tokenizer(sentence)
    return jsonify({"tokens": tokens})



@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    sentence = data.get("text", "").strip()
    if not sentence:
        return jsonify({"error": "Empty input"}), 400

    tokens = tokenizer(sentence)
    token_string = '\n'.join(tokens)

    prompt = (
        f"The following Chinese sentence has already been tokenized into individual words, one per line:\n\n"
        f"{token_string}\n\n"
        f"Please do the following:\n"
        f"1. Translate the entire sentence fluently into natural English.\n"
        f"2. Then, translate each token one by one, preserving the original order.\n\n"
        f"For names and places (e.g. '余瑞冬', '哥伦比亚省'), use transliteration or the official translation.\n"
        f"Do not skip any token. Do not reorder anything.\n"
        f"Your output must be plain text only, without any headings or labels.\n\n"
        f"Structure:\n"
        f"<your English translation here>\n"
        f"token1: translation1\n"
        f"token2: translation2\n"
        f"..."
    )

    messages = [
        {
            "role": "system",
            "content": (
                "You are a precise and consistent Chinese-English translation assistant.\n"
                "You always translate full sentences and provide literal word-by-word translations.\n"
                "You return only plain text. No formatting, no JSON, no extra headings like 'Full translation:'."
            )
        },
        {
            "role": "user",
            "content": prompt
        }
    ]

    response_text = chat_with_deepseek(messages).strip()
    lines = response_text.split('\n')

    full_translation = ""
    token_translations_map = {}

    for line in lines:
        if not full_translation and ":" not in line and len(line.strip()) > 10:
            full_translation = line.strip()
        elif ":" in line:
            parts = line.split(":", 1)
            token = parts[0].strip()
            translation = parts[1].strip()
            token_translations_map[token] = translation

    token_list = []
    for idx, token in enumerate(tokens):
        pinyin = ' '.join(lazy_pinyin(token, style=Style.TONE))
        token_list.append({
            "position": idx,
            "token": token,
            "pinyin": pinyin,
            "translation": token_translations_map.get(token, "")
        })

    return jsonify({
        "full_translation": full_translation,
        "token_list": token_list
    })



if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5005)
