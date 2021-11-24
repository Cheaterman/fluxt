from flask import Flask

app = Flask(__name__)

@app.route('/')
def api_index():
    return {'message': 'Hello!'}
