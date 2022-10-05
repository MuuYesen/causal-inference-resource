import numpy as np
from sklearn.utils import class_weight

import os
os.environ['CUDA_VISIBLE_DEVICES']='0'

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Activation
from tensorflow.keras.layers import RepeatVector, TimeDistributed
from tensorflow.keras.layers import ConvLSTM2D, Flatten

import tensorflow as tf
physical_devices = tf.config.experimental.list_physical_devices('GPU')
tf.config.experimental.set_memory_growth(physical_devices[0], True)

class ConvLSTM(object):

    def __init__(self, input_shape):
        super(ConvLSTM, self).__init__()

        param_net = {}
        param_net['filters'] = 16
        param_net['kernel_size'] = (1,3)
        param_net['strides'] = (1, 1)
        param_net['padding'] = 'valid'
        param_net['activation'] = 'relu'
        param_net['use_bias'] = True
        param_net['kernel_initializer'] = 'glorot_uniform'
        param_net['data_format'] = 'channels_last'
        param_net['input_shape'] = input_shape

        self.param_net = param_net

        seq = Sequential()
        seq.add(
            ConvLSTM2D(filters=self.param_net['filters'], kernel_size=self.param_net['kernel_size'], strides=self.param_net['strides'],
                       input_shape=self.param_net['input_shape'], padding=self.param_net['padding'],
                       activation=self.param_net['activation'],
                       use_bias=self.param_net['use_bias'], kernel_initializer=self.param_net['kernel_initializer'],
                       data_format=self.param_net['data_format'],
                       return_sequences=True))
        seq.add(
            ConvLSTM2D(filters=self.param_net['filters'], kernel_size=self.param_net['kernel_size'], strides=(1,1),
                       padding=self.param_net['padding'], activation=self.param_net['activation'], use_bias=self.param_net['use_bias'],
                       kernel_initializer=self.param_net['kernel_initializer'], return_sequences=True))
        seq.add(Flatten())
        seq.add(RepeatVector(1))
        seq.add(LSTM(200, activation='relu', return_sequences=True))
        seq.add(TimeDistributed(Dense(100, activation='relu')))
        seq.add(TimeDistributed(Dense(1)))
        seq.add(Flatten())
        seq.add(Dense(1))
        seq.add(Activation('sigmoid'))
        self.model = seq

    def train(self, X_train, Y_train, X_test, Y_test):
        cw = class_weight.compute_class_weight(class_weight='balanced',
                                               classes=np.unique(Y_train),
                                               y=Y_train)
        cw = dict(enumerate(cw))

        self.model.compile(
            loss='binary_crossentropy',
            optimizer='adam')

        self.model.fit(X_train, Y_train, validation_data=(X_test, Y_test),
                      class_weight=cw, batch_size=16, epochs=100, verbose=1)
        return self

    def predict(self, X_test):
        Y_pre = self.model.predict(X_test).reshape(-1)
        return Y_pre

    def save(self, checkpoint):
        self.model.save(checkpoint)

    def load_weights(self, checkpoint):
        self.model.load_weights(checkpoint)

    def summary(self):
        self.model.summary()