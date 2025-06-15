from flask import Flask, request, jsonify
import hanlp

app = Flask(__name__)
tokenizer = hanlp.load('PKU_NAME_MERGED_SIX_MONTHS_CONVSEG')

API_KEY = "12345678-MVP"

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

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5005)
