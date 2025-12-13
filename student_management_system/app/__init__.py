from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from config.config import config_by_name

db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return User.query.get(int(user_id))

    # Register blueprints
    from app.views.auth import auth_bp
    from app.views.admin import admin_bp
    from app.views.student import student_bp
    from app.views.main import main_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(student_bp, url_prefix='/student')
    app.register_blueprint(main_bp)

    # Create tables
    with app.app_context():
        db.create_all()

        # Create default admin if not exists
        from app.models.user import User
        from app.models.admin import Administrator

        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                email='admin@example.com',
                full_name='System Administrator',
                role='admin'
            )
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            db.session.commit()

            admin = Administrator(
                user_id=admin_user.id,
                admin_code='ADMIN001',
                department='System Administration'
            )
            db.session.add(admin)
            db.session.commit()

    return app