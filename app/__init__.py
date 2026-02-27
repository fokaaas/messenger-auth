from flask import Flask

from app.config import SECRET_KEY
from app.services.database import init_db
from app.routes import registration_bp, login_bp, recovery_bp


def create_app():
    app = Flask(__name__)
    app.secret_key = SECRET_KEY

    init_db()

    app.register_blueprint(registration_bp)
    app.register_blueprint(login_bp)
    app.register_blueprint(recovery_bp)

    return app
