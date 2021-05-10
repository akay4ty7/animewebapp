import os
import cv2
import random
import numpy as np
import torch
import argparse
from shutil import copyfile
from edgeRemovalFiles.config import Config
from edgeRemovalFiles.edge_connect import EdgeConnect

def humanRemoval(mode=None):
    r"""starts the model
    """
    config = load_config(mode)

    # cuda visble devices
    os.environ['CUDA_VISIBLE_DEVICES'] = ','.join(str(e) for e in config.GPU)

    # init device
    if torch.cuda.is_available():
        config.DEVICE = torch.device("cuda")
        torch.backends.cudnn.benchmark = True   # cudnn auto-tuner
    else:
        config.DEVICE = torch.device("cpu")

    # set cv2 running threads to 1 (prevents deadlocks with pytorch dataloader)
    cv2.setNumThreads(0)

    # initialize random seed
    torch.manual_seed(config.SEED)
    torch.cuda.manual_seed_all(config.SEED)
    np.random.seed(config.SEED)
    random.seed(config.SEED)

    # build the model and initialize
    model = EdgeConnect(config)
    model.load()

    # model test
    print('\nstart testing...\n')
    model.test()


def load_config(mode=None):

    # If path for checkpoint not given
    path='./checkpointHumanRemoval'
    config_path = os.path.join(path, 'config.yml')

    # Load config file
    config = Config(config_path)

   
    # Test mode
    config.MODE = 2
    config.MODEL = 3
    config.OBJECTS = [15]
    config.SEG_DEVICE = 'cpu' if 'cpu' is not None else 'cuda'
    config.INPUT_SIZE = 800
    config.TEST_FLIST = 'static/client/img'

    config.TEST_EDGE_FLIST = './checkpointsremoval'
    config.RESULTS = 'static/client/img'

    return config

if __name__ == "__main__":
    main()
