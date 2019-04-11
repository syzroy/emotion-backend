"""
Created on Sep 22, 2018

@author: Yizhe Sun
"""

import os

from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO

from emotion.main.config import *


def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config['VIDEO_FOLDER'] = VIDEO_FOLDER
    app.config['MODEL_PATH'] = MODEL_PATH
    # cnn_model, lstm_model = load_model(app.config['MODEL_PATH'])

    from .main.controllers import blueprint
    app.register_blueprint(blueprint)
    # initialise socketio for web socket communication
    socketio = SocketIO(app, message_queue='redis://')

    return app, socketio
