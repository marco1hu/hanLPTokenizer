from flask import Flask
from .routes import register_routes
from .models import db
from .services.logger import setup_logger
from firebase_admin import credentials, initialize_app
import os
from .config import Config
from dotenv import load_dotenv
from .services.error_handlers import register_error_handlers


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # .env
    load_dotenv()

    # DB
    db.init_app(app)

    # Logging
    setup_logger(app)

    # Firebase init
    cred = credentials.Certificate("keys/ocrchineseapp-firebase-adminsdk-fbsvc-6d111a54f2.json")
    initialize_app(cred)

    # Routes
    register_routes(app)
    
    register_error_handlers(app)
    return app

    return app
