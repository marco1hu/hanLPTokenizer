from .tokenize import tokenize_bp
from .analyze import analyze_bp
from .analyze_with_pinyin import analyze_with_pinyin_bp
from .explain import explain_bp
from .upgrade_user import upgrade_user_bp
from .status import status_bp
from .downgrade_user import downgrade_user_bp

def register_routes(app):
    app.register_blueprint(tokenize_bp)
    app.register_blueprint(analyze_bp)
    app.register_blueprint(analyze_with_pinyin_bp)
    app.register_blueprint(explain_bp)
    app.register_blueprint(upgrade_user_bp)
    app.register_blueprint(status_bp)
    app.register_blueprint(downgrade_user_bp)
