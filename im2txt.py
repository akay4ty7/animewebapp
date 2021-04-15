# Copyright 2016 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
r"""Generate captions for images using default beam search parameters."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import math
import os


import tensorflow as tf

import configuration
import inference_wrapper
from inference_utils import caption_generator
from inference_utils import vocabulary

tf.logging.set_verbosity(tf.logging.INFO)

checkpoint_path = "im2txtFiles/model/newmodel.ckpt-2000000"
vocab_file = "im2txtFiles/wordCount/word_counts.txt"
input_files = "static/client/img/"


def rename_model_ckpt():

    BASE_DIR = '/Users/wlku/Documents/Developing/TensorFlow/Im2txt/'
    
    vars_to_rename = {
    "lstm/BasicLSTMCell/Linear/Matrix": "lstm/basic_lstm_cell/kernel",
    "lstm/BasicLSTMCell/Linear/Bias": "lstm/basic_lstm_cell/bias",
    }
    
    new_checkpoint_vars = {}
    
    reader = tf.train.NewCheckpointReader(checkpoint_path)
    for old_name in reader.get_variable_to_shape_map():
      if old_name in vars_to_rename:
        new_name = vars_to_rename[old_name]
      else:
        new_name = old_name

      print(old_name)
      new_checkpoint_vars[new_name] = tf.Variable(reader.get_tensor(old_name))

    init = tf.global_variables_initializer()
    saver = tf.train.Saver(new_checkpoint_vars)

    print("BASE_DIR = ", BASE_DIR)

    with tf.Session() as sess:
      sess.run(init)
      saver.save(sess, os.path.join(BASE_DIR, "data/model/Hugh/train/newmodel.ckpt-2000000"))
    print("checkpoint file rename successful... ")

# This definition is responsible for reading the image and producing descriptions.
# It is then translated into Japanese.
def im2txt(currentimagename):

  # Build the inference graph.
  g = tf.Graph()
  with g.as_default():
    model = inference_wrapper.InferenceWrapper()
    restore_fn = model.build_graph_from_config(configuration.ModelConfig(),
                                               checkpoint_path)
  g.finalize()

  # Create the vocabulary.
  vocab = vocabulary.Vocabulary(vocab_file)

  imageName = input_files + currentimagename
  filenames = []
  for file_pattern in imageName.split(","):
    filenames.extend(tf.gfile.Glob(file_pattern))
  tf.logging.info("Running caption generation on %d files matching %s",
                  len(filenames), imageName)

  with tf.Session(graph=g) as sess:
    # Load the model from checkpoint.
    restore_fn(sess)

    # Prepare the caption generator. Here we are implicitly using the default
    # beam search parameters. See caption_generator.py for a description of the
    # available beam search parameters.
    generator = caption_generator.CaptionGenerator(model, vocab)

    for filename in filenames:
      with tf.gfile.GFile(filename, "rb") as f:
        image = f.read()
      captions = generator.beam_search(sess, image)
      print("Captions for image %s:" % os.path.basename(filename))
      for i, caption in enumerate(captions):
        # Ignore begin and end words.
        sentence = [vocab.id_to_word(w) for w in caption.sentence[1:-1]]
        sentence = " ".join(sentence)
        return sentence

if __name__ == "__main__":
  tf.app.run()
