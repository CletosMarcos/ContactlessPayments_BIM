import enum
from datetime import datetime, timedelta
from sqlalchemy import Index, UniqueConstraint
from app.extensions import db

class IntentStatus(enum.Enum):
    OPEN="OPEN"; PARTIALLY_PAID="PARTIALLY_PAID"; PAID="PAID"; EXPIRED="EXPIRED"; CANCELLED="CANCELLED"
class PaymentMethod(enum.Enum):
    TAP="TAP"; QR="QR"
class PaymentStatus(enum.Enum):
    PENDING="PENDING"; APPROVED="APPROVED"; DECLINED="DECLINED"; REFUNDED="REFUNDED"

class PaymentIntent(db.Model):
    __tablename__ = "payment_intents"
    id = db.Column(db.BigInteger, primary_key=True)
    merchant_id = db.Column(db.BigInteger, db.ForeignKey("merchants.id"), nullable=False)
    pos_device_id = db.Column(db.BigInteger, db.ForeignKey("pos_devices.id"))
    amount_cents = db.Column(db.Integer, nullable=False)
    currency = db.Column(db.String(3), default="MZN", nullable=False)
    status = db.Column(db.Enum(IntentStatus), default=IntentStatus.OPEN, nullable=False)
    expires_at = db.Column(db.DateTime, default=lambda: datetime.utcnow()+timedelta(minutes=10))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    emvco_payload = db.Column(db.Text, nullable=False)
    ref = db.Column(db.String(36), unique=True, nullable=False)
    payments = db.relationship("Payment", back_populates="intent", lazy="select")
    __table_args__ = (Index("ix_intents_merchant_status", "merchant_id", "status"),)

class Payment(db.Model):
    __tablename__ = "payments"
    id = db.Column(db.BigInteger, primary_key=True)
    intent_id = db.Column(db.BigInteger, db.ForeignKey("payment_intents.id"), nullable=False)
    merchant_id = db.Column(db.BigInteger, db.ForeignKey("merchants.id"), nullable=False)
    pos_device_id = db.Column(db.BigInteger, db.ForeignKey("pos_devices.id"))
    method = db.Column(db.Enum(PaymentMethod), nullable=False)
    amount_cents = db.Column(db.Integer, nullable=False)
    currency = db.Column(db.String(3), default="MZN", nullable=False)
    status = db.Column(db.Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    auth_code = db.Column(db.String(12))
    network_txn_id = db.Column(db.String(40))
    brand = db.Column(db.String(20))
    last4 = db.Column(db.String(4))
    token_ref = db.Column(db.String(64))
    idempotency_key = db.Column(db.String(64), unique=True)
    meta = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    intent = db.relationship("PaymentIntent", back_populates="payments", lazy="joined")
    __table_args__ = (Index("ix_payments_merchant_status", "merchant_id", "status"),)

class PaymentSplit(db.Model):
    __tablename__ = "payment_splits"
    id = db.Column(db.BigInteger, primary_key=True)
    intent_id = db.Column(db.BigInteger, db.ForeignKey("payment_intents.id"), nullable=False)
    payment_id = db.Column(db.BigInteger, db.ForeignKey("payments.id"))
    amount_cents = db.Column(db.Integer, nullable=False)
    sequence = db.Column(db.Integer, default=1, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
