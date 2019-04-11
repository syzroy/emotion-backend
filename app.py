"""
Created on Dec 13, 2018

@author: Yizhe Sun
"""

import os
from gevent import monkey
monkey.patch_all()

from emotion import create_app, VIDEO_FOLDER, CAMERA_FOLDER, STATIC_FOLDER
from emotion.tasks import predict_frame

if not os.path.isdir(VIDEO_FOLDER):
    os.mkdir(VIDEO_FOLDER)

if not os.path.isdir(CAMERA_FOLDER):
    os.mkdir(CAMERA_FOLDER)

if not os.path.isdir(STATIC_FOLDER):
    os.mkdir(STATIC_FOLDER)

app, socketio = create_app()


# receive camera screenshots from websocket
@socketio.on('message')
def handle_message(image_base64, file_id):
    predict_frame.delay(image_base64, file_id)


if __name__ == '__main__':
    socketio.run(app)
