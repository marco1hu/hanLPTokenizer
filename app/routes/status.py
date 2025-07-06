from flask import Blueprint, jsonify
from ..services.auth import firebase_auth_required
from ..services.deepseek_client import chat_with_deepseek
from ..services.gpt_client import chat_with_chatgpt
import time

status_bp = Blueprint("status", __name__, url_prefix="/status")

@status_bp.route("", methods=["GET"])
@firebase_auth_required
def deepseek_status():
    results = {
        "deepseek": {"status": "ok", "latency_ms": None},
        "chatgpt": {"status": "ok", "latency_ms": None},
    }

    # Test DeepSeek
    try:
        start = time.time()
        chat_with_deepseek([{"role": "user", "content": "hello"}], temperature=0)
        results["deepseek"]["latency_ms"] = int((time.time() - start) * 1000)
    except Exception:
        results["deepseek"]["status"] = "down"

    # Test ChatGPT
    try:
        start = time.time()
        chat_with_chatgpt([{"role": "user", "content": "hello"}], temperature=0)
        results["chatgpt"]["latency_ms"] = int((time.time() - start) * 1000)
    except Exception:
        results["chatgpt"]["status"] = "down"

    http_code = 200 if results["deepseek"]["status"] == "ok" and results["chatgpt"]["status"] == "ok" else 503
    return jsonify(results), http_code

