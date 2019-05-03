"""
Created on Sep 22, 2018

@author: Yizhe Sun
"""

# Where to put the uploaded and generated files
VIDEO_FOLDER = 'video-uploads/'
# Where to load the trained LSTM model
MODEL_PATH = 'model/LSTM.h5'
# Where to put the analysis results for web camera
CAMERA_FOLDER = 'camera-analysis/'
# The URI for the database
DATABASE_URI = 'mysql+pymysql://ys51:!Zc2g9GRmy83Hm@klovia.cs.st-andrews.ac.uk/ys51_emotion'
# Where to put the static files
STATIC_FOLDER = 'static/'
# The size of preprocessing for images
IMG_SIZE = 100
# URL for the prediction server
SERVICE_URL = 'https://22a1e095.ngrok.io'

# Video formats accepted
ALLOWED_EXTENSIONS = {'mp4', 'mov'}

# HTTP response status codes
OK = 200
ERROR_NO_UPLOADED_FILE = 4001
VIDEO_TYPE_NOT_SUPPORTED = 4002
NO_VIDEO_ID = 4003
INVALID_VIDEO_ID = 4004
NO_FRAME_NO = 4005

classification_units = [
    'Inner brow raiser', 'Outer brow raiser', 'Brow lower', 'Upper lid raiser',
    'Cheek raiser', 'Lid tightener', 'Nose wrinkler', 'Upper lip raiser',
    'Lip corner puller', 'Dimpler', 'Lip corner depressor', 'Chin raiser',
    'Lip stretcher', 'Lip tightener', 'Lips part', 'Jaw drop', 'Lip suck',
    'Blink'
]

emotions = [
    "angry", "calm", "disgust", "fear", "sad", "happy", "neutral", "surprise"
]
