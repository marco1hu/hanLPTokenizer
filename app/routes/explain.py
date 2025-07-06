
from flask import Blueprint, request, jsonify, current_app as app, g
from ..services.auth import firebase_auth_required
from ..services.gpt_client import chat_with_chatgpt
from ..models.user import db
from datetime import date

explain_bp = Blueprint("explain", __name__, url_prefix="/explain")

@explain_bp.route("", methods=["POST"])
@firebase_auth_required
def explain():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    token = data.get("token", "").strip()
    sentence = data.get("sentence", "").strip()
    if not token or not sentence:
        return jsonify({"error": "Missing token or sentence"}), 400

    try:
        user = g.user
        if user.role == "free":
            if user.should_reset_explain_count():
                user.explain_count = 0
                user.last_explain_reset = date.today()

            if user.explain_count >= 3:
                return jsonify({
                    "error": "Free plan limit reached",
                    "message": "Max 3 explanations/day.",
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
        
        raw_output = chat_with_chatgpt(messages)
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

        required_fields = ["token", "pinyin", "meaning", "synonyms", "explanation", "example"]
        if not all(field in response_data for field in required_fields):
            raise ValueError("Missing fields in AI response")

        if user.role == "free":
            user.increment_explain_count()
        db.session.commit()

        return jsonify(response_data)

    except Exception as e:
        db.session.rollback()
        app.logger.exception(f"Errore su /explain: {str(e)}")
        return jsonify({"error": "Internal server error", "message": str(e)}), 500