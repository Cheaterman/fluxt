from flask import Flask
from flask_marshmallow_openapi import OpenAPISettings, OpenAPI  # type: ignore


def nuxtify(url: str) -> str:
    host, _, path = url.partition('/api/')
    return f'{host}/{path}'


def create_app(config: dict[str, str | float] | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_pyfile('config.py')

    if config:
        app.config.from_mapping(config)

    from .model import db, migrate
    db.init_app(app)
    migrate.init_app(app, db)

    # See https://github.com/marshmallow-code/apispec/issues/444
    import warnings
    warnings.filterwarnings(
        "ignore",
        message="Multiple schemas resolved to the name "
    )

    from .api import api
    app.register_blueprint(api)

    # XXX: Remove this for production
    from .demo import api
    app.register_blueprint(api)

    if (
        app.config.get('ENABLE_DOCS')
        # For coverage
        or app.config.get('TESTING')
    ):
        docs = OpenAPI(config=OpenAPISettings(
            api_name='Fluxt API',
            api_version='v1',
            app_package_name=f'{__name__}.api',
        ))
        docs.init_app(app)

    return app
