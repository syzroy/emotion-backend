"""
Created on Sep 22, 2018

@author: Yizhe Sun
"""

import sys
sys.path.append('/home/roy/Downloads/backend/')
import os
import uuid

from werkzeug.utils import secure_filename
import sqlalchemy as db

from emotion.main.config import ALLOWED_EXTENSIONS, DATABASE_URI, MODEL_PATH

# connect to database
engine = db.create_engine(DATABASE_URI)
connection = engine.connect()
metadata = db.MetaData()

# frame_analysis table
frame_analysis = db.Table('frame_analysis',
                          metadata,
                          autoload=True,
                          autoload_with=engine)
# video table
video = db.Table('video', metadata, autoload=True, autoload_with=engine)


# Check whether the file is within the supported format
def allowed_file(filename):
    return '.' in filename and filename.rsplit(
        '.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Save the uploaded video file to disk
def save_file(file, dir_path):
    file_id = str(uuid.uuid4())
    filename = secure_filename(file_id)
    file_path = os.path.join(dir_path, filename)
    file.save(file_path)
    return file_path, file_id


# Silently remove a file
def remove_file(file_path):
    try:
        os.remove(file_path)
    except OSError:
        pass
