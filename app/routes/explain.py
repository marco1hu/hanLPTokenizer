from flask import Blueprint, request, jsonify, current_app as app, g
from ..services.auth import firebase_auth_required
from ..services.gpt_client import chat_with_chatgpt
from ..models.user import db
from datetime import date
from ..utils.explain_prompts import get_explain_messages
from pypinyin import lazy_pinyin, Style

explain_bp = Blueprint("explain", __name__, url_prefix="/explain")

@explain_bp.route("", methods=["POST"])
@firebase_auth_required
def explain():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    token = data.get("token", "").strip()
    sentence = data.get("sentence", "").strip()
    lang = data.get("lang", "en")
    
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

        messages = get_explain_messages(lang=lang, word=token, sentence=sentence)
        raw_output = chat_with_chatgpt(messages)

        response_data = {}
        synonyms_raw = []

        for line in raw_output.strip().splitlines():
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            key = key.strip().lower()
            value = value.strip()

            if key == "synonyms":
                synonyms_raw = [s.strip() for s in value.split(",") if s.strip()]
                response_data["synonyms"] = synonyms_raw
            elif key in ["meaning", "explanation", "example"]:
                response_data[key] = value

        required_fields = ["meaning", "synonyms", "explanation", "example"]
        if not all(field in response_data for field in required_fields):
            raise ValueError("Missing fields in AI response")

       
        response_data["example_pinyin"] = " ".join(
            lazy_pinyin(response_data["example"], style=Style.TONE)
        )

    
        response_data["synonyms_pinyin"] = [
            " ".join(lazy_pinyin(s, style=Style.TONE)) for s in synonyms_raw
        ]

        if user.role == "free":
            user.increment_explain_count()
        db.session.commit()

        return jsonify(response_data)

    except Exception as e:
        db.session.rollback()
        app.logger.exception(f"Errore su /explain: {str(e)}")
        return jsonify({"error": "Internal server error", "message": str(e)}), 500
