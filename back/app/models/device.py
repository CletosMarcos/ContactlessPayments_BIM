import enum
from datetime import datetime
from sqlalchemy import Enum, Index
from app.extensions import db

class Platform(enum.Enum):
    ANDROID = "ANDROID"
    IOS = "IOS"
    WEB = "WEB"  # PWA

class PosDevice(db.Model):
    __tablename__ = "pos_devices"

    id = db.Column(db.BigInteger, primary_key=True)
    merchant_id = db.Column(db.BigInteger, db.ForeignKey("merchants.id"), nullable=False)

    public_id = db.Column(db.String(64), unique=True, nullable=False)  # ex.: uuid curto
    model = db.Column(db.String(80), nullable=True)
    platform = db.Column(Enum(Platform), default=Platform.ANDROID, nullable=False)
    nfc_supported = db.Column(db.Boolean, default=False, nullable=False)

    is_active = db.Column(db.Boolean, default=True, nullable=False)
    registered_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_seen_at = db.Column(db.DateTime, nullable=True)

    merchant = db.relationship("Merchant", back_populates="devices", lazy="joined")

    __table_args__ = (Index("ix_pos_devices_merchant", "merchant_id"),)