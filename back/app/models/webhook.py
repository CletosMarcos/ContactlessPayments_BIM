from datetime import datetime
from sqlalchemy import Index
from app.extensions import db

class WebhookEvent(db.Model):
    __tablename__ = "webhook_events"
    id = db.Column(db.BigInteger, primary_key=True)
    direction = db.Column(db.String(3), nullable=False)  # 'IN' ou 'OUT'
    provider = db.Column(db.String(40))                  # PSP/banco
    event_type = db.Column(db.String(60))
    url = db.Column(db.String(255))                      # para OUT
    headers = db.Column(db.JSON)
    payload = db.Column(db.JSON)
    status_code = db.Column(db.Integer)
    attempts = db.Column(db.Integer, default=0, nullable=False)
    next_retry_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    external_id = db.Column(db.String(64), unique=True)  # id do provedor (para idempotência)

    __table_args__ = (
        Index("ix_webhook_events_provider", "provider"),
        Index("ix_webhook_events_created", "created_at"),
    )
