from flask import Flask, request, jsonify
import hanlp
from pypinyin import lazy_pinyin, Style
import os
from dotenv import load_dotenv
from deepseek_client import chat_with_deepseek, chat_with_fallback, chat_with_chatgpt
import logging
from logging.handlers import RotatingFileHandler
import firebase_admin
from firebase_admin import credentials, auth as firebase_auth
from models import db, User
import openai 
from functools import wraps
from flask import request, jsonify
from models import db, User  
from flask import g
import json
from datetime import date



#gestione firebase
cred = credentials.Certificate("keys/ocrchineseapp-firebase-adminsdk-fbsvc-6d111a54f2.json")
firebase_admin.initialize_app(cred)


app = Flask(__name__)

#gestione db users
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

#creazione cartella logs
if not os.path.exists('logs'):
    os.mkdir('logs')
file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=5)
file_handler.setLevel(logging.INFO)

formatter = logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
)
file_handler.setFormatter(formatter)
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)
app.logger.info('App startup')

tokenizer = hanlp.load('LARGE_ALBERT_BASE')
load_dotenv()
DK_API_KEY = os.getenv("DEEPSEEK_API_KEY")


def firebase_auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization', None)
        if not auth_header or not auth_header.startswith('Bearer '):
            app.logger.warning(f"Missing or invalid Authorization header from {request.remote_addr} on {request.path}")
            return jsonify({"error": "Missing or invalid Authorization header"}), 401

        id_token = auth_header.split(' ')[1]

        try:
            decoded_token = firebase_auth.verify_id_token(id_token)
            uid = decoded_token.get('uid')
            email = decoded_token.get('email')

            user = User.query.filter_by(firebase_uid=uid).first()
            if not user:
                user = User(firebase_uid=uid, email=email)
                db.session.add(user)
                db.session.commit()
                app.logger.info(f"New user created in DB: {email} ({uid})")

            g.user = user
            return f(*args, **kwargs)

        except Exception as e:
            app.logger.warning(f"Invalid Firebase token from {request.remote_addr} on {request.path}: {str(e)}")
            return jsonify({"error": "Invalid Firebase token", "details": str(e)}), 401

    return decorated_function


@app.route('/tokenize', methods=['POST'])
@firebase_auth_required
def tokenize():
    data = request.get_json()
    # Logga la richiesta ricevuta
    app.logger.info(f"Richiesta ricevuta su /tokenize da {request.remote_addr} con dati: {data}")
    sentence = data.get('text', '').strip()
    if not sentence:
        app.logger.warning(f"Richiesta a /tokenize con input vuoto da {request.remote_addr}")
        return jsonify({"error": "Empty input"}), 400
    try:
        tokens = tokenizer(sentence)
        # Log del risultato della tokenizzazione
        app.logger.info(f"Tokenizzazione completata su /tokenize: {tokens}")
        return jsonify({"tokens": tokens})
    except Exception as e:
        # Se succede un errore interno
        app.logger.exception(f"Errore durante la tokenizzazione su /tokenize: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500
    
    
@app.route('/analyze', methods=['POST'])
@firebase_auth_required
def analyze():
    data = request.get_json()
    app.logger.info(f"Richiesta ricevuta su /analyze da {request.remote_addr} con dati: {data}")

    sentence = data.get("text", "").strip()
    if not sentence:
        app.logger.warning(f"Input vuoto ricevuto su /analyze da {request.remote_addr}")
        return jsonify({"error": "Empty input"}), 400

    try:
        tokens = [token.strip() for token in tokenizer(sentence)]
        app.logger.info(f"Tokenizzazione completata su /analyze: {tokens}")

        if len(tokens) > 60:
            return jsonify({
                "error": "Too many tokens",
                "message": "The sentence is too long. Please split it into shorter parts (max 60 tokens)."
            }), 413

        messages = [
            {
                "role": "system",
                "content": (
                    "You are a precise Chinese-English translator. "
                    "Return only plain text. No markdown, no commentary."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Sentence: {sentence}\n"
                    f"Tokens: {tokens}\n\n"
                    f"Your task:\n"
                    f"1. Translate the sentence into natural English.\n"
                    f"2. Then, write each token followed by a colon and its literal translation, one per line.\n\n"
                    f"Example format:\n"
                    f"Natural English translation here.\n"
                    f"token1: translation1\n"
                    f"token2: translation2\n"
                    f"...\n"
                )
            }
        ]

        response_text = chat_with_deepseek(messages).strip()
        app.logger.info("Risposta ricevuta per /analyze")

        lines = response_text.splitlines()
        full_translation = ""
        token_translations = {}

        for line in lines:
            if not full_translation and ':' not in line and len(line.strip()) > 10:
                full_translation = line.strip()
            elif ':' in line:
                parts = line.split(':', 1)
                token = parts[0].strip()
                translation = parts[1].strip()
                token_translations[token] = translation

        token_list = []
        for idx, token in enumerate(tokens):
            token_list.append({
                "position": idx,
                "token": token,
                "translation": token_translations.get(token, "")
            })

        return jsonify({
            "full_translation": full_translation,
            "token_list": token_list
        })

    except Exception as e:
        app.logger.exception(f"Errore su /analyze: {str(e)}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500


@app.route("/explain", methods=["POST"])
@firebase_auth_required
def explain():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    app.logger.info(f"Richiesta ricevuta su /explain da {request.remote_addr} con dati: {data}")

    token = data.get("token", "").strip()
    sentence = data.get("sentence", "").strip()

    if not token or not sentence:
        app.logger.warning(f"Input mancante su /explain da {request.remote_addr}")
        return jsonify({"error": "Missing token or sentence"}), 400

    try:
        user = g.user
        today = date.today()

        if user.role == "free":
            if user.last_explain_reset != today:
                user.explain_count = 0
                user.last_explain_reset = today

            if user.explain_count >= 3:
                app.logger.info(f"Limite spiegazioni superato per utente {user.firebase_uid}")
                return jsonify({
                    "error": "Free plan limit reached",
                    "message": "You can use up to 3 explanations per day with the free plan. Upgrade to Plus to unlock unlimited explanations.",
                    "explain_count": user.explain_count
                }), 402

        messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful and precise Chinese assistant. "
                    "Respond only in plain English text. No markdown, no JSON, no Chinese commentary."
                )
            },
            {
                "role": "user",
                "content": f"""
        Explain the Chinese word “{token}” in the sentence: “{sentence}”.

        Respond with exactly these fields, in plain English, one per line:
        token: ...
        pinyin: ... (with tone marks, e.g. zhù míng)
        meaning: ...
        synonyms: ... (comma-separated Chinese words)
        explanation: ... (in English)
        example: ... (short Chinese sentence)

        Plain text only. One field per line. No Chinese explanation.
        """
            }
        ]



        app.logger.info(f"Chiamata a GPT per utente {user.firebase_uid} – token '{token}'")
        raw_output = chat_with_chatgpt(messages)
        app.logger.info("Risposta ricevuta da GPT")

        # Parsing della risposta plain text
        response_data = {}
        for line in raw_output.strip().splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip().lower()
                value = value.strip()
                if key == "synonyms":
                    response_data[key] = [s.strip() for s in value.split(",")]
                else:
                    response_data[key] = value

        # Controllo campi minimi richiesti
        required_fields = ["token", "pinyin", "meaning", "synonyms", "explanation", "example"]
        if not all(field in response_data for field in required_fields):
            raise ValueError("Missing fields in AI response")

        # Aggiorna contatore se free
        if user.role == "free":
            user.explain_count += 1
        db.session.commit()

        return jsonify(response_data)

    except Exception as e:
        db.session.rollback()
        app.logger.exception(f"Errore su /explain per utente {g.user.firebase_uid}: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500

        
    

@app.route('/analyze_with_pinyin', methods=['POST'])
@firebase_auth_required
def analyze_with_pinyin():
    data = request.get_json()
    app.logger.info(f"Richiesta ricevuta su /analyze_with_pinyin da {request.remote_addr} con dati: {data}")

    sentence = data.get("text", "").strip()
    if not sentence:
        app.logger.warning(f"Input vuoto ricevuto su /analyze_with_pinyin da {request.remote_addr}")
        return jsonify({"error": "Empty input"}), 400

    try:
        tokens = [token.strip() for token in tokenizer(sentence)]
        app.logger.info(f"Tokenizzazione completata su /analyze_with_pinyin: {tokens}")

        if len(tokens) > 60:
            return jsonify({
                "error": "Too many tokens",
                "message": "The sentence is too long. Please split it into shorter parts (max 60 tokens)."
            }), 413

        messages = [
            {
                "role": "system",
                "content": (
                    "You are a precise Chinese-English translator. "
                    "Return only plain text. No markdown, no commentary."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Sentence: {sentence}\n"
                    f"Tokens: {tokens}\n\n"
                    f"Your task:\n"
                    f"1. Translate the sentence into natural English.\n"
                    f"2. Then, write each token followed by a colon and its literal translation, one per line.\n\n"
                    f"Example format:\n"
                    f"Natural English translation here.\n"
                    f"token1: translation1\n"
                    f"token2: translation2\n"
                    f"...\n"
                )
            }
        ]

        response_text = chat_with_deepseek(messages).strip()
        app.logger.info("Risposta ricevuta per /analyze_with_pinyin")

        lines = response_text.splitlines()
        full_translation = ""
        token_translations = {}

        for line in lines:
            if not full_translation and ':' not in line and len(line.strip()) > 10:
                full_translation = line.strip()
            elif ':' in line:
                parts = line.split(':', 1)
                token = parts[0].strip()
                translation = parts[1].strip()
                token_translations[token] = translation

        token_list = []
        for idx, token in enumerate(tokens):
            pinyin = ' '.join(lazy_pinyin(token, style=Style.TONE))  
            token_list.append({
                "position": idx,
                "token": token,
                "pinyin": pinyin,
                "translation": token_translations.get(token, "")
            })

        return jsonify({
            "full_translation": full_translation,
            "token_list": token_list
        })

    except Exception as e:
        app.logger.exception(f"Errore su /analyze_with_pinyin: {str(e)}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

@app.route("/upgrade_user", methods=["POST"])
@firebase_auth_required
def upgrade_user():
    user = g.user  


    if user.email != "testuser@example.com":
        app.logger.warning(f"Tentativo di upgrade da utente non autorizzato: {user.email}")
        return jsonify({"error": "Unauthorized"}), 403

    try:
        user.role = "premium"
        db.session.commit()
        app.logger.info(f"Utente {user.email} aggiornato a premium.")
        return jsonify({"message": f"{user.email} è ora un utente premium."})
    except Exception as e:
        db.session.rollback()
        app.logger.exception(f"Errore durante upgrade utente: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@app.route("/deepseek-status", methods=["GET"])
@firebase_auth_required
def deepseek_status():
    try:
        chat_with_deepseek([{"role": "user", "content": "hello"}], temperature=0)
        return jsonify({"status": "ok"})
    except Exception:
        return jsonify({"status": "down"}), 503


@app.errorhandler(Exception)
def handle_exception(e):
    app.logger.exception("Unhandled Exception: %s", e)
    return jsonify({
        "status": "error",
        "message": "Internal Server Error",
        "details": str(e) if app.debug else "Something went wrong on the server."
    }), 500

@app.errorhandler(400)
def bad_request_error(e):
    app.logger.warning(f"Bad Request: {str(e)}")
    return jsonify({
        "status": "error",
        "message": "Bad Request",
        "details": str(e)
    }), 400

@app.errorhandler(401)
def unauthorized_error(e):
    app.logger.warning(f"Unauthorized: {str(e)}")
    return jsonify({
        "status": "error",
        "message": "Unauthorized",
        "details": str(e)
    }), 401


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5005)
