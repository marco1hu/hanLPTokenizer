from flask import Blueprint, jsonify, g, current_app as app
from ..services.auth import firebase_auth_required
from ..models.user import db


downgrade_user_bp = Blueprint("downgrade_user", __name__, url_prefix="/downgrade_user")


@downgrade_user_bp.route("", methods=["POST"])
@firebase_auth_required
def downgrade_user():
    user = g.user
    if user.email != "testuser@example.com":
        app.logger.warning(f"Tentativo di downgrade da utente non autorizzato: {user.email}")
        return jsonify({"error": "Unauthorized"}), 403

    try:
        user.role = "free"
        db.session.commit()
        app.logger.info(f"Utente {user.email} aggiornato a free.")
        return jsonify({"message": f"{user.email} è ora un utente free."})
    except Exception as e:
        db.session.rollback()
        app.logger.exception(f"Errore durante downgrade utente: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500