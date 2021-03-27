import os
import numpy as np
import cv2
import tensorflow as tf
from removal.model import *




def remove():
    mask = np.load(r'./static/client/mask.npy')
    img = np.load(r'./static/client/img.npy')
    x, y = img.shape[0:2]
    img = cv2.resize(img, (400, 400))
    img = img / 255
    mask = np.dstack([mask, mask, mask])
    print(mask)
    print(True ^ mask)
    masked_img = (True ^ mask) * np.array(img)
    input_image_masked = masked_img[:, :, [2, 1, 0]]
    shape = np.array(input_image_masked).shape
    input_tensor = np.array(input_image_masked).reshape(1, shape[0], shape[1], shape[2])
    tf.reset_default_graph()
    pretrained_model = 'removal/pretrained_model'
    sess = tf.Session()
    isTraining = tf.placeholder(tf.bool)
    images_placeholder = tf.placeholder(tf.float32, shape=[1, 400, 400, 3], name="images")
    model = Model()
    reconstruction_ori = model.build_reconstruction(images_placeholder, isTraining)
    saver = tf.train.Saver(max_to_keep=100)
    saver.restore(sess, pretrained_model)
    output_tensor = sess.run(
        reconstruction_ori,
        feed_dict={
            images_placeholder: input_tensor,
            isTraining: False
        }
    )
    filtered_image = np.array(output_tensor)[0, :, :, :].astype(float)
    filtered_image = cv2.resize(filtered_image, (y, x))
    cv2.imwrite(r'./static/client/removal_img.jpg', ((filtered_image[:,:,[2, 1, 0]]) * 255))


