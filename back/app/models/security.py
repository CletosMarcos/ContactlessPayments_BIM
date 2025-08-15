from datetime import datetime
from sqlalchemy import Index
from app.extensions import db

class LoginAttempt(db.Model):
    __tablename__ = "login_attempts"
    id = db.Column(db.BigInteger, primary_key=True)
    context = db.Column(db.String(12), nullable=False)   # 'BUYER' ou 'POS'
    buyer_user_id = db.Column(db.BigInteger, db.ForeignKey("buyer_users.id"))
    operator_user_id = db.Column(db.BigInteger, db.ForeignKey("operator_users.id"))
    success = db.Column(db.Boolean, default=False, nullable=False)
    reason = db.Column(db.String(60))     # ex.: BAD_PIN, LOCKED, OK
    ip = db.Column(db.String(45))         # IPv4/IPv6
    user_agent = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_login_attempts_context", "context"),
    )
