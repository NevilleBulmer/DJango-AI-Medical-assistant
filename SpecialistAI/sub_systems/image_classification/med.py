import keras
import cv2
from keras.models import Sequential
from skimage.io import imread, imsave
from keras.layers import Dense, Dropout, Flatten
from keras.layers import Conv2D, MaxPooling2D
from keras.utils import to_categorical
from keras.preprocessing import image
from keras.layers.convolutional import Convolution2D, ZeroPadding2D
from keras.applications.vgg16 import decode_predictions
from keras.optimizers import SGD
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from keras.utils import np_utils
from keras.models import load_model
from sklearn.model_selection import train_test_split

class VGG16Classification:

    def VGG_16(weights_path=None):
        model = Sequential()
        model.add(ZeroPadding2D((1,1),input_shape=(256,256,1)))
        model.add(Convolution2D(64, 3, 3, activation='sigmoid'))
        model.add(ZeroPadding2D((1,1)))
        model.add(Convolution2D(64, 3, 3, activation='sigmoid'))
        model.add(MaxPooling2D((2,2), strides=(2,2)))

        model.add(ZeroPadding2D((1,1)))
        model.add(Convolution2D(128, 3, 3, activation='sigmoid'))
        model.add(ZeroPadding2D((1,1)))
        model.add(Convolution2D(128, 3, 3, activation='sigmoid'))
        model.add(MaxPooling2D((2,2), strides=(2,2)))

        model.add(ZeroPadding2D((1,1)))
        model.add(Convolution2D(256, 3, 3, activation='sigmoid'))
        model.add(ZeroPadding2D((1,1)))
        model.add(Convolution2D(256, 3, 3, activation='sigmoid'))
        model.add(ZeroPadding2D((1,1)))
        model.add(Convolution2D(256, 3, 3, activation='sigmoid'))
        model.add(MaxPooling2D((2,2), strides=(2,2)))

        model.add(ZeroPadding2D((1,1)))
        model.add(Convolution2D(512, 3, 3, activation='sigmoid'))
        model.add(ZeroPadding2D((1,1)))
        model.add(Convolution2D(512, 3, 3, activation='sigmoid'))
        model.add(ZeroPadding2D((1,1)))
        model.add(Convolution2D(512, 3, 3, activation='sigmoid'))
        model.add(MaxPooling2D((2,2), strides=(2,2)))

        model.add(ZeroPadding2D((1,1)))
        model.add(Convolution2D(512, 3, 3, activation='sigmoid'))
        model.add(ZeroPadding2D((1,1)))
        model.add(Convolution2D(512, 3, 3, activation='sigmoid'))
        model.add(ZeroPadding2D((1,1)))
        model.add(Convolution2D(512, 3, 3, activation='sigmoid'))
        model.add(MaxPooling2D((2,2), strides=(2,2)))

        model.add(Flatten())
        model.add(Dense(10, activation='sigmoid'))
        model.add(Dropout(0.5))
        model.add(Dense(10, activation='sigmoid'))
        model.add(Dropout(0.5))
        model.add(Dense(10, activation='softmax'))

        if weights_path:
            model.load_weights(weights_path)

        return model
    def PredictVGG(SegImage,path1):
        windowsize_r=256
        windowsize_c=256
        pa=path1.split('\\')
        pa1=pa[len(pa)-1]
        pa2=pa1.split('.')
        DataTrain = np.zeros((3713,windowsize_r, windowsize_c,1), dtype=np.uint8)
        DataTest = np.zeros((1,windowsize_r, windowsize_c,1), dtype=np.uint8)
        LabelTrain=np.zeros((3713,1), dtype=np.uint8)
        LabelTest=np.zeros((500,1), dtype=np.uint8)


        labelClass=np.load('Label.npy')
        train_image = []
        for i in range(1,labelClass.shape[1]):
            dim = (256,256)
            img = imread('pred/'+str(i)+'.jpg')
            DataTrain[i,:,:,0]=cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
            LabelTrain[i]=labelClass[0,i-1]

       for i in range(1,500):
           img = imread('pred/'+str(i)+'.jpg')
           DataTest[i,:,:,0]=cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
           LabelTest[i]=labelClass[0,i-1]
        DataTest[0,:,:,0]=cv2.resize(SegImage, dim, interpolation = cv2.INTER_AREA)
        DataTrain /= 255
        DataTest /= 255
        LabelTrain = np_utils.to_categorical(LabelTrain, 10)
        LabelTest = np_utils.to_categorical(LabelTest, 10)
        VGG_model = VGG16Classification.VGG_16()
        VGG_model.compile(loss="categorical_crossentropy",optimizer="adam",metrics=["accuracy"])
        VGG_model.fit(DataTrain, LabelTrain,batch_size=32, nb_epoch=1, verbose=1)
        VGG_model.save("VGG16model.h5")
        VGG_model = load_model('VGG16model.h5')
        VGG_model.summary()
        PredictClass=(VGG_model.predict(DataTest))
        PredictClass1=labelClass[0,int(pa2[0])]
       score = VGG_model.evaluate(DataTest, LabelTest, verbose=0)
       print(score[1]*100)
        return PredictClass1
