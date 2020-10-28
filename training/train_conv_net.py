import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import pickle
import cv2
from selfdriving.model.conv_net_model import *

import tensorflow as tf

from sklearn.model_selection import train_test_split

def train(X_train, Y_train, X_val, Y_val, max_epochs=20, batch_size=8, save_path=None, restore=False):
    batch_num = len(X_train)//batch_size
    with tf.Session() as sess:
        if restore:
            saver.restore(sess, save_path+'conv_net.ckpt')
        else:
            sess.run(tf.global_variables_initializer())
        for epoch in range(max_epochs):
            avg_loss = []
            for batch in range(batch_num):
                b_start = batch*batch_size
                b_end = (batch+1)*batch_size
                batch_x = X_train[b_start:b_end]
                batch_y = Y_train[b_start:b_end].reshape(-1,1)
                #print(batch_x.shape, batch_y.shape)
                _, train_loss = sess.run([optimizer, loss], feed_dict={x:batch_x, y:batch_y, keep_prob:0.8})
                avg_loss.append(train_loss)
                print('\rEpoch {} - Batch {}/{} - Loss: {:.5f} - Avg Loss: {:.5f} '.format(epoch+1, batch+1, batch_num, train_loss, np.mean(avg_loss)),end='')
            
            avg_val_loss = []
            for batch in range(len(X_val)//batch_size):
                b_start = batch*batch_size
                b_end = (batch+1)*batch_size
                val_loss = sess.run(loss, feed_dict={x:X_train[b_start:b_end], y:Y_train[b_start:b_end].reshape(-1,1), keep_prob:1.0})
                avg_val_loss.append(val_loss)

            print('- Val Loss: {:.5f} '.format(np.mean(avg_val_loss)))

            np.random.seed(547)
            np.random.shuffle(X_train)
            np.random.seed(547)
            np.random.shuffle(Y_train)
            
            if not os.path.exists('save_path'):
                os.makedirs('save_path')
            saver.save(sess, save_path+'/conv_net.ckpt')

train_vars = tf.trainable_variables()
network = conv_net(x, keep_prob)
loss = tf.sqrt(tf.reduce_mean(tf.square(tf.subtract(network, y))))
optimizer = tf.train.AdamOptimizer(1e-4).minimize(loss)
saver = tf.train.Saver()

SAVE_PATH='conv_net/conv_net_v1'
BATCH_SIZE=16
EPOCHS=20

y_pred = []
with tf.Session() as sess:
    saver.restore(sess, 'conv_net/conv_net_v2/conv_net.ckpt')
    for frame, angle in zip(X, Y):
        pred = sess.run(network, feed_dict={x:[frame], keep_prob:1.0})[0][0]
        y_pred.append(pred)
        '''
        print('Prediction: {:.4f} Actual: {:.4f}'.format(pred, angle))
        cv2.imshow('Frame', frame.astype(np.float32))
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        '''

plt.plot([i for i in range(100)], Y[:100])
plt.plot([i for i in range(100)], y_pred[:100])
plt.show()

