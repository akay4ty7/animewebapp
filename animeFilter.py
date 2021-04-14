import argparse
from tools.utils import *
import os
from tqdm import tqdm
from glob import glob
import time
import numpy as np
from animeFilterFiles import generator
os.environ["CUDA_VISIBLE_DEVICES"] = "0"

# This definition is used to filter the image into an anime style.
def animeFilter(img_size=[256,256]):
    checkpoint_dir = 'checkpointAnimeFilter/generator_Hayao_weight'
    result_dir = 'static/client/img'
    test_dir = 'static/client/img'
    check_folder(result_dir)
    test_files = glob('{}/*.*'.format(test_dir))

    test_real = tf.placeholder(tf.float32, [1, None, None, 3], name='test')

    with tf.variable_scope("generator", reuse=False):
            test_generated = generator.G_net(test_real).fake

    saver = tf.train.Saver()

    gpu_options = tf.GPUOptions(allow_growth=True)
    with tf.Session(config=tf.ConfigProto(allow_soft_placement=True, gpu_options=gpu_options)) as sess:
        ckpt = tf.train.get_checkpoint_state(checkpoint_dir)  # checkpoint file information
        if ckpt and ckpt.model_checkpoint_path:
            ckpt_name = os.path.basename(ckpt.model_checkpoint_path)  # first line

            saver.restore(sess, os.path.join(checkpoint_dir, ckpt_name))

        begin = time.time()
        for sample_file  in tqdm(test_files) :
            sample_image = np.asarray(load_test_data(sample_file, img_size))
            image_path = os.path.join(result_dir,'{0}'.format(os.path.basename(sample_file)))
            fake_img = sess.run(test_generated, feed_dict = {test_real : sample_image})
            #adjustBrightness
            save_images(fake_img, image_path, sample_file)
        end = time.time()
        print(f'test-time: {end-begin} s')
        print(f'one image test time : {(end-begin)/len(test_files)} s')

