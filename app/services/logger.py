import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logger(app):
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler(
        app.config['LOG_FILE'], maxBytes=10240, backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    )
    file_handler.setFormatter(formatter)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('App startup')
