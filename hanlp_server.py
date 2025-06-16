from flask import Flask, request, jsonify
import hanlp
from pypinyin import lazy_pinyin, Style
import os

app = Flask(__name__)
tokenizer = hanlp.load('PKU_NAME_MERGED_SIX_MONTHS_CONVSEG')

API_KEY = os.getenv("HANLP_API_KEY")

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
    sentence = data.get("text", "")
    tokens = tokenizer(sentence)
    pinyins = lazy_pinyin(tokens, style=Style.TONE)
    
    result = [
        {"token": token, "pinyin": pinyin}
        for token, pinyin in zip(tokens, pinyins)
    ]
    return jsonify(result)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5005)
