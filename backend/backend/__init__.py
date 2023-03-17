from flask import Flask


def create_app(config=None):
    app = Flask(__name__)
    app.config.from_pyfile('config.py')

    if config:
        app.config.from_mapping(config)

    from .model import db, migrate
    db.init_app(app)
    migrate.init_app(app, db)

    from .api import api
    app.register_blueprint(api)

    return app
