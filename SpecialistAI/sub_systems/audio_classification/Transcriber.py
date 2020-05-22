# import keras
from tensorflow import keras
import tensorflow as tf
import random #
import os
import librosa
import numpy as np
import sys

import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# def __init__(self):
#load the trained model
h55 = BASE_DIR + '/audio_classification/speechRecogModel.h5'
try:

    config = tf.ConfigProto(
        device_count={'GPU': 1},
        intra_op_parallelism_threads=1,
        allow_soft_placement=True
    )

    session = tf.Session(config=config)

    keras.backend.set_session(session)

    model = keras.models.load_model(h55)
except(FileNotFoundError):
    print('Please ensure the trained model "speechRecogModel.h5" is present in the directory.')

def __getClass(index):

    switch = {
        0: 'Bed',
        1: 'Bird',
        2: 'Cat',
        3: 'Dog',
        4: 'Down',
        5: 'Eight',
        6: 'Five',
        7: 'Four',
        8: 'Go',
        9: 'Happy',
        10: 'House',
        11: 'Left',
        12: 'Marvin',
        13: 'Nine',
        14: 'No',
        15: 'Off',
        16: 'On',
        17: 'One',
        18: 'Right',
        19: 'Seven',
        20: 'Sheila',
        21: 'Six',
        22: 'Stop',
        23: 'Three',
        24: 'Tree',
        25: 'Two',
        26: 'Up',
        27: 'Wow',
        28: 'Yes',
        29: 'Zero'}

    return switch.get(index, "Error, this word is not recognised")

def transcribe(path): #takes filepath of a 1-second wav file as input
    with session.as_default():
        with session.graph.as_default():
            sound, sampleRate = librosa.load(path, sr = 16000)
            sound = librosa.resample(sound, sampleRate, 8000)

            try:
                sound = np.array(sound).reshape(-1, 8000, 1) #check the clip is the correct length
            except(ValueError):
                print('Error, please ensure sound clip is 1 second long.\n')
                raise SystemExit()

            classify = model.predict(sound)
            prediction = np.argmax(classify)
            word = __getClass(prediction)

            print('The spoken word is: ' + word + '.\n')

            return ('The spoken word is: ' + word + '.\n')