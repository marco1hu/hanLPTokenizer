from flask import request, jsonify, g, current_app
from firebase_admin import auth as firebase_auth
from functools import wraps
from ..models.user import User, db

def firebase_auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization', None)
        if not auth_header or not auth_header.startswith('Bearer '):
            current_app.logger.warning("Missing or invalid Authorization header")
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
                current_app.logger.info(f"New user created in DB: {email} ({uid})")

            g.user = user
            return f(*args, **kwargs)

        except Exception as e:
            current_app.logger.warning(f"Invalid Firebase token: {str(e)}")
            return jsonify({"error": "Invalid Firebase token", "details": str(e)}), 401

    return decorated_function
