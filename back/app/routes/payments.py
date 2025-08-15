from flask import Blueprint, request, jsonify, abort
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from app.extensions import db
from app.models import (
    Payment, PaymentIntent, PaymentMethod, PaymentStatus, IntentStatus, TransactionEvent
)

bp = Blueprint("payments", __name__)


def _amounts(intent: PaymentIntent):
    paid = sum(p.amount_cents for p in intent.payments if p.status == PaymentStatus.APPROVED)
    remaining = max(intent.amount_cents - paid, 0)
    return paid, remaining


def _ensure_open(intent: PaymentIntent):
    if intent.status in (IntentStatus.CANCELLED, IntentStatus.EXPIRED):
        abort(409, description=f"intent is {intent.status.value}")
    if intent.expires_at and datetime.utcnow() > intent.expires_at:
        intent.status = IntentStatus.EXPIRED
        db.session.commit()
        abort(409, description="intent expired")


@bp.post("/charge")
def charge():
    data = request.get_json(force=True)
    intent_id = int(data["intent_id"])
    method = PaymentMethod(data["method"])  # 'TAP'/'QR'
    idempotency_key = data.get("idempotency_key")
    token_ref = data.get("token_ref"); brand = data.get("brand"); last4 = data.get("last4")

    intent = PaymentIntent.query.get_or_404(intent_id)
    _ensure_open(intent)

    # Idempotência
    if idempotency_key:
        existing = Payment.query.filter_by(idempotency_key=idempotency_key).first()
        if existing:
            _, remaining = _amounts(intent)
            return jsonify({
                "payment_id": existing.id,
                "intent_status": intent.status.value,
                "payment_status": existing.status.value,
                "auth_code": existing.auth_code,
                "amount_remaining_cents": remaining
            }), 200

    paid, remaining = _amounts(intent)
    amount = data.get("amount_cents")
    amount = int(amount) if amount is not None else remaining
    if amount <= 0: abort(400, description="invalid amount (<=0)")
    if amount > remaining: abort(400, description=f"amount {amount} exceeds remaining {remaining}")

    pay = Payment(
        intent_id=intent.id, merchant_id=intent.merchant_id, pos_device_id=intent.pos_device_id,
        method=method, amount_cents=amount, currency=intent.currency,
        status=PaymentStatus.APPROVED, auth_code="OK1234", network_txn_id="RRN-DEMO",
        brand=brand, last4=last4, token_ref=token_ref, idempotency_key=idempotency_key, meta={"mock": True}
    )
    db.session.add(pay); db.session.flush()
    db.session.add(TransactionEvent(payment_id=pay.id, event_type="AUTHORIZED", details={"code":"00"}))
    db.session.add(TransactionEvent(payment_id=pay.id, event_type="CAPTURED", details={"batch":"D0"}))

    intent.status = IntentStatus.PAID if amount == remaining else IntentStatus.PARTIALLY_PAID

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        if idempotency_key:
            existing = Payment.query.filter_by(idempotency_key=idempotency_key).first()
            if existing:
                _, remaining = _amounts(intent)
                return jsonify({
                    "payment_id": existing.id,
                    "intent_status": intent.status.value,
                    "payment_status": existing.status.value,
                    "auth_code": existing.auth_code,
                    "amount_remaining_cents": remaining
                }), 200
        raise

    _, remaining_final = _amounts(intent)
    return jsonify({
        "payment_id": pay.id,
        "intent_status": intent.status.value,
        "payment_status": pay.status.value,
        "auth_code": pay.auth_code,
        "amount_remaining_cents": remaining_final
    }), 201