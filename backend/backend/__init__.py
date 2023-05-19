from flask import Flask


class ConfigurationError(Exception):
    pass


def create_app(config=None):
    app = Flask(__name__)
    app.config.from_pyfile('config.py')

    if config:
        app.config.from_mapping(config)

    if not app.config.get('ADMIN_PASSWORD'):
        raise ConfigurationError(
            'You cannot leave your admin area unprotected: '
            'set ADMIN_PASSWORD environment variable.'
        )

    from .model import db, migrate
    db.init_app(app)
    migrate.init_app(app, db)

    from .api import api
    app.register_blueprint(api)

    return app
