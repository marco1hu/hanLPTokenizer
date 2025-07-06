from flask import jsonify, current_app as app

def register_error_handlers(app):

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
