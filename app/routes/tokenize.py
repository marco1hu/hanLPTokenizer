from flask import Blueprint, request, jsonify, current_app as app
from ..services.tokenizer import tokenize_text
from ..services.auth import firebase_auth_required

tokenize_bp = Blueprint("tokenize", __name__, url_prefix="/tokenize")

@tokenize_bp.route("", methods=["POST"])
@firebase_auth_required
def tokenize():
    data = request.get_json()
    sentence = data.get("text", "").strip()
    if not sentence:
        return jsonify({"error": "Empty input"}), 400
    try:
        tokens = tokenize_text(sentence)
        return jsonify({"tokens": tokens})
    except Exception as e:
        app.logger.exception(f"Errore su /tokenize: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500