from flask_sqlalchemy import SQLAlchemy
from datetime import date

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firebase_uid = db.Column(db.String(128), unique=True, nullable=False)
    email = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='free')  # 'free' o 'premium'
    explain_count = db.Column(db.Integer, default=0)
    last_explain_reset = db.Column(db.Date, default=None)

    def is_premium(self):
        return self.role == "premium"

    def should_reset_explain_count(self):
        return self.last_explain_reset != date.today()

    def increment_explain_count(self):
        if self.should_reset_explain_count():
            self.explain_count = 1
            self.last_explain_reset = date.today()
        else:
            self.explain_count += 1
