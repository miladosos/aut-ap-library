from flask import Flask
from app.routes.books import books_bp
from app.routes.users import users_bp
from app.routes.reservation import reservation_bp

def create_app():
    app = Flask(__name__)
    app.register_blueprint(books_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(reservation_bp)
    return app
