from flask import Flask, jsonify
from .config import Config
from .extensions import init_extensions
from .routes.intents import bp as intents_bp
from .routes.payments import bp as payments_bp
from .models import * 

def create_app(config_class: type = Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    init_extensions(app)
    
    app.register_blueprint(intents_bp, url_prefix="/intents")
    app.register_blueprint(payments_bp, url_prefix="/payments")

    @app.get("/health")
    def health():
        return jsonify(ok=True)

    return app
