#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "Flask",
#     "Flask-SSE"
# ]
# ///
from flask import Flask, Response
from flask_sse import sse
import time

app = Flask(__name__)
app.config["REDIS_URL"] = "redis://localhost:6379/0"
app.register_blueprint(sse, url_prefix='/stream')

@app.route('/')
def index():
    return "SSE server is running. Connect to /stream to receive events."

@app.route('/send')
def send_event():
    sse.publish({"message": "Hello!"}, type='greeting')
    return "Message sent!"

if __name__ == '__main__':
    app.run(debug=True, threaded=True)
