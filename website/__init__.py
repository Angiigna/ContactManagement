from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy import inspect, text

db = SQLAlchemy()


def create_app(test_config=None):
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'change-this-development-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    if test_config:
        app.config.update(test_config)

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .model import User, Contacts

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    with app.app_context():
        db.create_all()
        _upgrade_legacy_schema()

    return app


def _upgrade_legacy_schema():
    """Add fields introduced after the original local database schema."""
    columns = {column['name']
               for column in inspect(db.engine).get_columns('contacts')}
    if 'email' not in columns:
        db.session.execute(
            text("ALTER TABLE contacts ADD COLUMN email VARCHAR(120) NOT NULL DEFAULT ''"))
    if 'owner_id' not in columns:
        db.session.execute(
            text("ALTER TABLE contacts ADD COLUMN owner_id INTEGER"))
    first_user = db.session.execute(
        text('SELECT id FROM user ORDER BY id LIMIT 1')).scalar()
    if first_user is not None:
        db.session.execute(text('UPDATE contacts SET owner_id = :owner_id WHERE owner_id IS NULL'), {
                           'owner_id': first_user})
    db.session.commit()
