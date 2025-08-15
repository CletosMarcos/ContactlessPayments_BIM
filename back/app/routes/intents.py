from flask import Blueprint, request, jsonify, send_file, abort
from uuid import uuid4
from datetime import datetime
import io, qrcode
from app.extensions import db
from app.models import Merchant, PaymentIntent, IntentStatus, Payment, PaymentStatus
from app.utils.emvco import build_emvco_dynamic

bp = Blueprint("intents", __name__)

@bp.post("")
def create_intent():
    data = request.get_json(force=True)
    merchant_id = data["merchant_id"]
    pos_device_id = data.get("pos_device_id")
    amount_cents = int(data["amount_cents"])
    currency = data.get("currency", "MZN")

    merchant = Merchant.query.get_or_404(merchant_id)
    ref = str(uuid4())

    payload = build_emvco_dynamic({
        "merchant_account": f"MER-{merchant_id}",
        "ref": ref,
        "amount": f"{amount_cents/100:.2f}",
        "merchant_name": merchant.legal_name[:25],
        "city": "MAPUTO",
        "country": "MZ",
        "currency": "943",
    })

    intent = PaymentIntent(
        merchant_id=merchant_id,
        pos_device_id=pos_device_id,
        amount_cents=amount_cents,
        currency=currency,
        emvco_payload=payload,
        ref=ref,
        status=IntentStatus.OPEN,
    )
    db.session.add(intent)
    db.session.commit()

    return jsonify({
        "intent_id": intent.id,
        "status": intent.status.value,
        "amount_cents": intent.amount_cents,
        "currency": intent.currency,
        "ref": intent.ref,
        "emvco_payload": intent.emvco_payload,
        "expires_at": intent.expires_at.isoformat() + "Z"
    }), 201

@bp.get("/<int:intent_id>")
def get_intent(intent_id: int):
    intent = PaymentIntent.query.get_or_404(intent_id)
    return jsonify({
        "intent_id": intent.id,
        "status": intent.status.value,
        "amount_cents": intent.amount_cents,
        "currency": intent.currency,
        "ref": intent.ref,
        "expires_at": intent.expires_at.isoformat() + "Z"
    })

def _maybe_expire_intent(intent: PaymentIntent):
    if intent.expires_at and datetime.utcnow() > intent.expires_at and intent.status in (IntentStatus.OPEN, IntentStatus.PARTIALLY_PAID):
        intent.status = IntentStatus.EXPIRED
        db.session.commit()

@bp.get("/lookup")
def lookup_by_ref():
    ref = request.args.get("ref")
    if not ref: abort(400, description="missing ref")
    intent = PaymentIntent.query.filter_by(ref=ref).first_or_404()
    _maybe_expire_intent(intent)
    return jsonify({"intent_id": intent.id, "status": intent.status.value})

@bp.get("/<int:intent_id>/summary")
def intent_summary(intent_id: int):
    intent = PaymentIntent.query.get_or_404(intent_id)
    _maybe_expire_intent(intent)
    paid = sum(p.amount_cents for p in intent.payments if p.status == PaymentStatus.APPROVED)
    return jsonify({
        "intent_id": intent.id,
        "status": intent.status.value,
        "amount_total_cents": intent.amount_cents,
        "amount_paid_cents": paid,
        "amount_remaining_cents": max(intent.amount_cents - paid, 0),
        "expires_at": intent.expires_at.isoformat() + "Z" if intent.expires_at else None
    })

@bp.get("/<int:intent_id>/qr.png")
def qr_png(intent_id: int):
    intent = PaymentIntent.query.get_or_404(intent_id)
    img = qrcode.make(intent.emvco_payload)
    buf = io.BytesIO(); img.save(buf, format="PNG"); buf.seek(0)
    return send_file(buf, mimetype="image/png")