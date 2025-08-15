from datetime import datetime
from sqlalchemy import Index, UniqueConstraint
from app.extensions import db

class OperatorUser(db.Model):
    __tablename__ = "operator_users"
    id = db.Column(db.BigInteger, primary_key=True)
    merchant_id = db.Column(db.BigInteger, db.ForeignKey("merchants.id"), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120))
    role = db.Column(db.String(20), default="OPERATOR", nullable=False)  # OPERATOR/MANAGER/ADMIN
    password_hash = db.Column(db.String(128))  # se precisares de login no POS
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_login_at = db.Column(db.DateTime)

    __table_args__ = (
        Index("ix_operator_users_merchant", "merchant_id"),
        UniqueConstraint("merchant_id", "email", name="uq_operator_email_per_merchant"),
    )
