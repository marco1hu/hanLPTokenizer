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
    sentence = data.get("text", "")
    tokens = tokenizer(sentence)
    result = []
    for token in tokens:
        # Calcola il pinyin per ciascun carattere della parola
        pinyin_list = lazy_pinyin(token, style=Style.TONE)
        pinyin = ' '.join(pinyin_list)
        result.append({
            "token": token,
            "pinyin": pinyin,
            "aa": DK_API_KEY
        })
    
    return jsonify(result)




@app.route('/test', methods=['GET'])
def test():
    prompt = (
        "Translate the following Chinese sentence into English:\n"
        "对于这笔交易，各方都希望尽快完成。尽管马洛塔在周六没有透露太多信息，"
        "但邦尼确实接近加盟国米，如今只剩一些奖金条款需要进行商谈。帕尔马希望国米能满足2500万欧元的要价，"
        "球员本人已和国米达成一致，两家俱乐部也非常接近达成协议。\n\n"
        "Only return the English translation as plain text. No explanation, no JSON, no formatting."
    )

    messages = [
        {
            "role": "system",
            "content": "You are a linguistic assistant specialized in Chinese. Respond only with plain English translations when asked."
        },
        {
            "role": "user",
            "content": prompt
        }
    ]

    response_text = chat_with_deepseek(messages)
    return jsonify({"translation": response_text.strip()})




if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5005)
