"""

This script takes a sample from the 2dfv.dat file (containing images of galaxies) and plots them. Galaxy images are 50x50
By Austin Shen
06/06/2018

"""

# -----------------------------------------------------------------------
# libraries

# tensorflow interface
import keras
import keras.callbacks
from keras import backend as K
from keras.models import Sequential, load_model, model_from_json
from keras.layers import Dense, Dropout, Flatten, Conv2D, MaxPooling2D
from keras.utils import np_utils

# system
import os.path
import sys
import argparse

# other packages
import numpy as np
import random
# import matplotlib
# matplotlib.use('Agg')
# import matplotlib.pyplot as plt

# written packages
import y_conversion as conversion

# -----------------------------------------------------------------------
# constants

# argument parser from command line
ap = argparse.ArgumentParser()
ap.add_argument("-e", "--epochs", required=True, help='number of epochs')
args = vars(ap.parse_args())
epochs = int(args['epochs'])

# Choosing parameters
batch_size = 32
num_classes = 1
print('epochs = %s, batch size = %s' % (epochs, batch_size))

# path to training data files
path_train = 'm1.dir_9_density/'

# path to test data files (for the training process)
path_test = 'm1.dir_8_density/'

# parameters (model)
n_mesh=50
nmodel=90000
img_rows, img_cols = n_mesh, n_mesh
n_mesh2=n_mesh*n_mesh-1
n_mesh3=n_mesh*n_mesh
input_shape = (img_rows, img_cols, 1)

# -----------------------------------------------------------------------
# function

# read function for map data
def read_data(path):

	# update to terminal
	print('reading data from: ' + str(path))

	# read files
	with open(path+'2dfv.dat') as f:
		lines=f.readlines()
	with open(path+'2dfvn.dat') as f:
		lines1=f.readlines()
	X=np.zeros((nmodel,n_mesh3))
	y=np.zeros((nmodel,num_classes))

	# For 2D density map data
	ibin=0
	jbin=-1
	for num,j in enumerate(lines):
		jbin=jbin+1
		tm=j.strip().split()
		X[ibin,jbin]=float(tm[0])
		if jbin == n_mesh2:
			ibin+=1
			jbin=-1

	# Y output
	ibin=0
	for num,j in enumerate(lines1[1:]):
		tm=j.strip().split()
		### Need to choose variable of interest ###
		### tm[0] <- vrel, tm[1] <- rho ###
		if (num_classes == 1):
			y[ibin,0]=float(tm[0])
		elif (num_classes == 2):
			y[ibin,0]=float(tm[0])
			y[ibin,1]=float(tm[1])
		ibin+=1

	# reshape
	X = X.reshape(X.shape[0], img_rows, img_cols, 1)

	# return data
	return(X, y)

# -----------------------------------------------------------------------
# reading training data

# extract training data
print('reading training data')
(x_train, y_train) = read_data(path_train)

# extracting test data
print('reading test data')
(x_test, y_test) = read_data(path_test)

# conversions where necessary
y_train = conversion.v_to_v2(y_train)
y_test = conversion.v_to_v2(y_test)

# -----------------------------------------------------------------------
# training models

print("Training model")

# Model Architecture
model = Sequential()
model.add(Conv2D(32, kernel_size=(3, 3),
                 activation='relu',
                 input_shape=input_shape))
model.add(Conv2D(64, (3, 3), activation='relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.25))
model.add(Flatten())
model.add(Dense(128, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(num_classes, activation='linear'))
model.compile(loss='mean_squared_error',
              optimizer=keras.optimizers.Adadelta(),
			  metrics=['accuracy'])
history = model.fit(x_train, y_train, batch_size=batch_size, epochs=epochs,
          verbose=1, validation_data=(x_test, y_test))

# -----------------------------------------------------------------------
# save model weights

print("Saving model weights")

# weights and models
model.save_weights("m1.dir_9_e300_joint_rho_weights.h5")
model.save("m1.dir_9_e300_joint_rho_model.h5")

# -----------------------------------------------------------------------
# plot results

sys.exit()

print("Plotting performance")

# summarize history for accuracy
plt.plot(history.history['acc'])
plt.plot(history.history['val_acc'])
plt.title('model accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.savefig('m1.dir_9_e300_accuracy.png')
plt.close()

# summarize history for loss
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('model loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.savefig('m1.dir_9_e300_loss.png')
plt.close()

# -----------------------------------------------------------------------