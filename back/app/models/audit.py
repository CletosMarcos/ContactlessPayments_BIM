from datetime import datetime
from sqlalchemy import Index, UniqueConstraint
from app.extensions import db

class TransactionEvent(db.Model):
    __tablename__ = "transaction_events"
    id = db.Column(db.BigInteger, primary_key=True)
    payment_id = db.Column(db.BigInteger, db.ForeignKey("payments.id"), nullable=False)
    event_type = db.Column(db.String(40), nullable=False)
    details = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    __table_args__ = (Index("ix_tx_events_payment", "payment_id"),)

class SettlementBatch(db.Model):
    __tablename__ = "settlement_batches"
    id = db.Column(db.BigInteger, primary_key=True)
    merchant_id = db.Column(db.BigInteger, db.ForeignKey("merchants.id"), nullable=False)
    business_date = db.Column(db.Date, nullable=False)
    total_gross_cents = db.Column(db.BigInteger, default=0, nullable=False)
    total_fees_cents = db.Column(db.BigInteger, default=0, nullable=False)
    total_net_cents = db.Column(db.BigInteger, default=0, nullable=False)
    status = db.Column(db.String(20), default="READY", nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    __table_args__ = (UniqueConstraint("merchant_id","business_date", name="uq_settlement_per_day"),)
