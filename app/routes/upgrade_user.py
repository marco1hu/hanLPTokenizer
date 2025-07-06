from flask import Blueprint, jsonify, g, current_app as app
from ..services.auth import firebase_auth_required
from ..models.user import db

upgrade_user_bp = Blueprint("upgrade_user", __name__, url_prefix="/upgrade_user")

@upgrade_user_bp.route("", methods=["POST"])
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