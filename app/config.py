import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///users.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    GPT_API_KEY = os.getenv("GPT_API_KEY")
    LOG_FILE = "logs/app.log"
