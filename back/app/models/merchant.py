from datetime import datetime
from sqlalchemy import Index
from app.extensions import db

class Merchant(db.Model):
    __tablename__ = "merchants"
    id = db.Column(db.BigInteger, primary_key=True)
    legal_name = db.Column(db.String(120), nullable=False)
    nuit = db.Column(db.String(20))
    iban = db.Column(db.String(34))
    status = db.Column(db.String(20), default="ACTIVE", nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    __table_args__ = (Index("ix_merchants_status", "status"),)

class PosDevice(db.Model):
    __tablename__ = "pos_devices"
    id = db.Column(db.BigInteger, primary_key=True)
    merchant_id = db.Column(db.BigInteger, db.ForeignKey("merchants.id"), nullable=False)
    public_id = db.Column(db.String(64), unique=True, nullable=False)
    model = db.Column(db.String(80))
    platform = db.Column(db.Enum("ANDROID","IOS","WEB", name="platform"), default="ANDROID", nullable=False)
    nfc_supported = db.Column(db.Boolean, default=True, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    registered_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_seen_at = db.Column(db.DateTime)
    __table_args__ = (Index("ix_pos_devices_merchant", "merchant_id"),)
