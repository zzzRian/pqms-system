import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Por favor inicie sesión para continuar."

def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)

    from app.models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from app.routes.auth import auth_bp
    from app.routes.users import users_bp
    from app.routes.production import production_bp
    from app.routes.stats import stats_bp
    from app.routes.iso import iso_bp
    from app.routes.training import training_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.claims import claims_bp
    from app.routes.reports import reports_bp
    from app.routes.traceability import traceability_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp, url_prefix="/users")
    app.register_blueprint(production_bp, url_prefix="/production")
    app.register_blueprint(stats_bp, url_prefix="/stats")
    app.register_blueprint(iso_bp, url_prefix="/iso")
    app.register_blueprint(training_bp, url_prefix="/training")
    app.register_blueprint(dashboard_bp, url_prefix="/dashboard")
    app.register_blueprint(claims_bp, url_prefix="/claims")
    app.register_blueprint(reports_bp, url_prefix="/reports")
    app.register_blueprint(traceability_bp, url_prefix="/traceability")

    @app.context_processor
    def inject_globals():
        from datetime import datetime
        return {"current_year": datetime.now().year}

    return app
