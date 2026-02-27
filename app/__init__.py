from flask import Flask

from app.config import SECRET_KEY
from app.services.database import init_db
from app.routes import registration_bp


def create_app():
    app = Flask(__name__)
    app.secret_key = SECRET_KEY

    init_db()

    app.register_blueprint(registration_bp)

    return app
