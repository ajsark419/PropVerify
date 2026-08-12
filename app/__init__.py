import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect

from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
csrf = CSRFProtect()

login_manager.login_view = "auth.login"
login_manager.login_message_category = "warning"


def create_app(config_class=Config):
    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.config.from_object(config_class)

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(os.path.join(app.config["UPLOAD_FOLDER"], "ids"), exist_ok=True)
    os.makedirs(os.path.join(app.config["UPLOAD_FOLDER"], "ownership"), exist_ok=True)
    os.makedirs(os.path.join(app.config["UPLOAD_FOLDER"], "properties"), exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    from app import models  # noqa: F401

    @login_manager.user_loader
    def load_user(user_id):
        return models.User.query.get(int(user_id))

    from app.routes.main import bp as main_bp
    from app.routes.auth import bp as auth_bp
    from app.routes.properties import bp as properties_bp
    from app.routes.verifications import bp as verifications_bp
    from app.routes.admin import bp as admin_bp
    from app.routes.messages import bp as messages_bp
    from app.routes.uploads import bp as uploads_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(properties_bp, url_prefix="/properties")
    app.register_blueprint(verifications_bp, url_prefix="/verifications")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(messages_bp, url_prefix="/messages")
    app.register_blueprint(uploads_bp, url_prefix="/files")

    from app.template_helpers import register_template_helpers
    register_template_helpers(app)

    with app.app_context():
        db.create_all()
        from app.seed import seed_default_admin
        seed_default_admin()

    return app
