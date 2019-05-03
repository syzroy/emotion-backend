from __future__ import absolute_import, unicode_literals
import sys
sys.path.append('/home/roy/Downloads/backend/')
import os
import base64
import shutil
import pickle

import numpy as np
import pandas as pd
import sqlalchemy as db
from flask_socketio import SocketIO
import requests
from PIL import Image
from keras.preprocessing import image

from emotion.main.config import *
from emotion.main.utils import remove_file, engine, frame_analysis
from emotion.celery import app


# analyse frame for action unit and facial expression
@app.task()
def predict_frame(image_base64, file_id):
    out_path = CAMERA_FOLDER + file_id + '/'
    os.mkdir(out_path)

    data = image_base64[23:]
    file_path = out_path + file_id + '.jpg'
    with open(file_path, 'wb') as f:
        f.write(base64.b64decode(data))

    openface = "OpenFace/FaceLandmarkImg"
    command = openface + ' -f ' + file_path + ' -out_dir ' + out_path
    os.system(command)
    csv_path = out_path + file_id + '.csv'
    df = pd.read_csv(csv_path, index_col=0)
    df = df.loc[:, ' AU01_c':]
    labels = [l + ' Classification' for l in classification_units]
    df.columns = labels
    au = [file_id]
    for _, row in df.iterrows():
        au.append(row.to_json())

    # start input pipline for prediction
    img = image.load_img(out_path + file_id + '_aligned/' +
                         'face_det_000000.bmp',
                         target_size=(IMG_SIZE, IMG_SIZE))
    conn = requests.post(SERVICE_URL,
                         data=pickle.dumps(img),
                         headers={'Content-Type': 'application/octet-stream'})
    if conn.ok:
        data = conn.json()
        au.append(data['result'][0])
        au.append(emotions)
    else:
        print(conn.content)
    # send result to the frontend
    socketio = SocketIO(message_queue='redis://')
    socketio.emit('message', au)
    shutil.rmtree(out_path)


# Preprocess and analyse the video
# Then Store the results to the database
@app.task()
def process_video(path):
    # use OpenFace to extract frames and action unit results
    result_path = path + '-processed'
    os.mkdir(result_path)
    command = 'OpenFace/FeatureExtraction -f ' + path + ' -nomask -out_dir ' + result_path
    os.system(command)
    remove_file(path)

    path_list = str(path).split('/')
    filename = path_list[len(path_list) - 1]

    # remove unnecessary files
    avi_path = os.path.join(result_path, filename + '.avi')
    hog_path = os.path.join(result_path, filename + '.hog')
    txt_path = os.path.join(result_path, filename + '_of_details.txt')
    remove_file(avi_path)
    remove_file(hog_path)
    remove_file(txt_path)

    # prepare dataframe
    csv_path = os.path.join(result_path, filename + '.csv')
    df = pd.read_csv(csv_path, index_col=0)
    df = df[df[' success'] == 1].loc[:, ' AU01_c':]
    labels = [l + ' Classification' for l in classification_units]
    df.columns = labels

    # delete unsuccessful images
    success_images = df.index.values
    aligned_path = os.path.join(result_path, filename + '_aligned/')
    static_path = STATIC_FOLDER + filename + '/'
    os.mkdir(static_path)
    img_paths = []
    for img in os.listdir(aligned_path):
        names = img.replace('.bmp', '').split('_')
        img_no = int(names[len(names) - 1])
        if img_no in success_images:
            img_path = os.path.join(aligned_path, img)
            dest = shutil.move(img_path, static_path)
            img_paths.append(dest)

    new_csv_path = os.path.join(STATIC_FOLDER, filename + '.csv')
    df.to_csv(new_csv_path)

    frame_data = []
    for frame_path in img_paths:
        # start input pipline for prediction
        img = image.load_img(frame_path, target_size=(IMG_SIZE, IMG_SIZE))
        conn = requests.post(
            SERVICE_URL,
            data=pickle.dumps(img),
            headers={'Content-Type': 'application/octet-stream'})

        # add all of the data into database
        data = conn.json()
        frame_data.append({
            'video_id': filename,
            'frame_path': frame_path,
            'csv_path': new_csv_path,
            'angry': data['result'][0][0],
            'calm': data['result'][0][1],
            'disgust': data['result'][0][2],
            'fear': data['result'][0][3],
            'sad': data['result'][0][4],
            'happy': data['result'][0][5],
            'neutral': data['result'][0][6],
            'surprise': data['result'][0][7]
        })

    connection = engine.connect()
    query = db.insert(frame_analysis)
    connection.execute(query, frame_data)
    connection.close()

    shutil.rmtree(result_path)
