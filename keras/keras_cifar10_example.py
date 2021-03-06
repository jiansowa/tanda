'''Train a simple deep CNN on the CIFAR10 small images dataset.

Replicated from `keras/examples/cifar10_cnn.py` to demonstrate 
`TANDAImageDataGenerator` usage. By default, we subsample to 10% of the training
data to benchmark data augmentation performance.
'''

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import keras

from experiments.cifar10.train import tfs
from experiments.utils import balanced_subsample
from keras.datasets import cifar10
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation, Flatten
from keras.layers import Conv2D, MaxPooling2D
from tanda_keras import TANDAImageDataGenerator
from utils import load_pretrained_tan

TAN_PATH = # TODO: Insert path here!
CONFIG_PATH = os.path.join(TAN_PATH, 'logs', 'run_log.json')
CHECKPOINT_PATH = os.path.join(TAN_PATH, 'checkpoints', 'tan_checkpoint')


batch_size = 32
num_classes = 10
epochs = 100
train_frac = 0.1


if __name__ == '__main__':
    # The data, shuffled and split between train and test sets:
    (x_train, y_train), (x_test, y_test) = cifar10.load_data()

    # Convert class vectors to binary class matrices.
    y_train = keras.utils.to_categorical(y_train, num_classes)
    y_test = keras.utils.to_categorical(y_test, num_classes)

    # Sample training data
    if 0 < train_frac < 1:
        n_per_class = int(x_train.shape[0] / num_classes * train_frac)
        x_train, y_train = balanced_subsample(x_train, y_train, n_per_class)
    print('x_train shape:', x_train.shape)
    print(x_train.shape[0], 'train samples')
    print(x_test.shape[0], 'test samples')

    

    model = Sequential()
    model.add(Conv2D(32, (3, 3), padding='same',
                     input_shape=x_train.shape[1:]))
    model.add(Activation('relu'))
    model.add(Conv2D(32, (3, 3)))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))

    model.add(Conv2D(64, (3, 3), padding='same'))
    model.add(Activation('relu'))
    model.add(Conv2D(64, (3, 3)))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))

    model.add(Flatten())
    model.add(Dense(512))
    model.add(Activation('relu'))
    model.add(Dropout(0.5))
    model.add(Dense(num_classes))
    model.add(Activation('softmax'))

    # initiate RMSprop optimizer
    opt = keras.optimizers.rmsprop(lr=0.0001, decay=1e-6)

    # Let's train the model using RMSprop
    model.compile(loss='categorical_crossentropy',
                  optimizer=opt,
                  metrics=['accuracy'])

    x_train = x_train.astype('float32')
    x_test = x_test.astype('float32')
    x_train /= 255
    x_test /= 255


    print('Loading TAN for real-time data augmentation.')
    # This will do preprocessing and realtime data augmentation using a TAN
    tan = load_pretrained_tan(CONFIG_PATH, CHECKPOINT_PATH, tfs)
    datagen = TANDAImageDataGenerator(tan)

    print('Training model.')
    # Fit the model on the batches generated by datagen.flow().
    model.fit_generator(datagen.flow(x_train, y_train,
                                     batch_size=batch_size),
                        epochs=epochs,
                        validation_data=(x_test, y_test),
                        workers=4)

    # Score trained model.
    scores = model.evaluate(x_test, y_test, verbose=1)
    print('Test loss:', scores[0])
    print('Test accuracy:', scores[1])
