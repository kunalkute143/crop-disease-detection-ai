from flask import Flask, render_template, request, session, redirect, url_for
from flask_login import current_user
import os

from config import Config

# Extensions
from extensions.db import db
from extensions.bcrypt import bcrypt
from extensions.login_manager import login_manager

# Models
from models.user import User
from models.prediction import Prediction

# Controllers
from controllers.auth_controller import auth_bp
from controllers.crop_controller import crop_bp
from controllers.chat_controller import chat_bp
from controllers.dashboard_controller import dashboard_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # -----------------------------
    # Initialize Extensions
    # -----------------------------
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    # -----------------------------
    # Login Manager Settings
    # -----------------------------
    login_manager.login_view = "auth.login"
    login_manager.login_message = "कृपया लॉगिन करा / Please login to continue"
    login_manager.login_message_category = "info"

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # -----------------------------
    # Register Blueprints
    # -----------------------------
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(crop_bp, url_prefix="/crop")
    app.register_blueprint(chat_bp, url_prefix="/chat")
    app.register_blueprint(dashboard_bp, url_prefix="/dashboard")

    # -----------------------------
    # Create Upload Folder
    # -----------------------------
    upload_folder = app.config.get("UPLOAD_FOLDER", "static/uploads")
    os.makedirs(upload_folder, exist_ok=True)  # ✅ exist_ok=True add केलं

    # -----------------------------
    # Create Database Tables
    # -----------------------------
    with app.app_context():
        db.create_all()
        print("✅ Database tables created successfully!")

    # -----------------------------
    # Routes
    # -----------------------------
    @app.route("/")
    def index():
        if "language" not in session:
            session["language"] = "en"
        return render_template("index.html")

    @app.route("/about")
    def about():
        return render_template("about.html")

    @app.route("/set_language/<lang>")
    def set_language(lang):
        if lang in ["en", "mr"]:
            session["language"] = lang
        return redirect(request.referrer or url_for("index"))

    # ========== RESULT PAGE ROUTE ==========
    @app.route("/crop/result")
    def crop_result():
        """Display crop disease detection result"""
        return render_template("crop/result.html")

    # ========== ERROR HANDLERS ==========
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template("500.html"), 500

    # ========== CONTEXT PROCESSOR ==========
    @app.context_processor
    def utility_processor():
        def get_language():
            return session.get("language", "en")
        return dict(get_language=get_language)

    return app


# -----------------------------
# Run Application
# -----------------------------
app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)