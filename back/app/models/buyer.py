import enum
from datetime import datetime
from sqlalchemy import Index, UniqueConstraint
from app.extensions import db

class PlatformEnum(enum.Enum):
    ANDROID = "ANDROID"
    IOS = "IOS"
    WEB = "WEB"

class CardStatus(enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"

class CardTokenType(enum.Enum):
    VAULT = "VAULT"     # token do cofre do PSP
    NETWORK = "NETWORK" # token da rede (MDES/VTS)
    WALLET = "WALLET"   # instrumento HCE interno (Android)

class BuyerUser(db.Model):
    __tablename__ = "buyer_users"
    id = db.Column(db.BigInteger, primary_key=True)
    phone = db.Column(db.String(20), nullable=False, unique=True)   # ex.: +25884...
    email = db.Column(db.String(120), unique=True)
    full_name = db.Column(db.String(120))
    pin_hash = db.Column(db.String(128))  # guarda hash do PIN (ex.: bcrypt)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_login_at = db.Column(db.DateTime)

    __table_args__ = (
        Index("ix_buyer_users_active", "is_active"),
    )

class BuyerDevice(db.Model):
    __tablename__ = "buyer_devices"
    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey("buyer_users.id"), nullable=False)
    device_public_id = db.Column(db.String(64), nullable=False)  # identificador do app/dispositivo
    platform = db.Column(db.Enum(PlatformEnum), default=PlatformEnum.ANDROID, nullable=False)
    model = db.Column(db.String(80))
    os_version = db.Column(db.String(40))
    is_trusted = db.Column(db.Boolean, default=True, nullable=False)
    push_token = db.Column(db.String(256))  # FCM/APNs, se usares
    registered_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_seen_at = db.Column(db.DateTime)

    __table_args__ = (
        UniqueConstraint("user_id", "device_public_id", name="uq_buyer_device_per_user"),
        Index("ix_buyer_devices_user", "user_id"),
    )

class PaymentCard(db.Model):
    __tablename__ = "buyer_payment_cards"
    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey("buyer_users.id"), nullable=False)

    token_type = db.Column(db.Enum(CardTokenType), nullable=False)  # VAULT/NETWORK/WALLET
    vault_token_ref = db.Column(db.String(64))        # se token_type = VAULT
    network_token_ref = db.Column(db.String(64))      # se token_type = NETWORK
    wallet_instrument_id = db.Column(db.String(64))   # se token_type = WALLET

    brand = db.Column(db.String(20))       # VISA/MASTERCARD/etc
    last4 = db.Column(db.String(4))
    exp_month = db.Column(db.SmallInteger) # opcional, conforme PSP permitir
    exp_year = db.Column(db.SmallInteger)
    issuer = db.Column(db.String(60))

    is_default = db.Column(db.Boolean, default=False, nullable=False)
    status = db.Column(db.Enum(CardStatus), default=CardStatus.ACTIVE, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_buyer_cards_user", "user_id"),
        # Evita tokens duplicados (se preenchidos). Como MySQL não permite unique com múltiplas colunas NULL de forma “clean”,
        # deixamos a validação final no app. Ainda assim, estes uniques ajudam muito:
        UniqueConstraint("user_id", "vault_token_ref", name="uq_card_vault_ref_per_user"),
        UniqueConstraint("user_id", "network_token_ref", name="uq_card_network_ref_per_user"),
        UniqueConstraint("user_id", "wallet_instrument_id", name="uq_card_wallet_ref_per_user"),
    )
