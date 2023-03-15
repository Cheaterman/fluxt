from flask import Flask


def create_app(config=None):
    app = Flask(__name__)

    if config:
        app.config.from_mapping(config)

    @app.route('/')
    def api_index():
        return {'message': 'Hello!'}

    return app
