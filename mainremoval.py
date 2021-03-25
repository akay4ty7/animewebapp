import os
import cv2
import random
import numpy as np
import torch
import argparse
from shutil import copyfile
from src.config import Config
from src.edge_connect import EdgeConnect

def main(mode=None):
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
    r"""loads model config



    parser = argparse.ArgumentParser()
    parser.add_argument('--path', '--checkpoints', type=str, default='./checkpointsremoval', help='model checkpoints path (default: ./checkpointsremoval)')
    parser.add_argument('--model', type=int, choices=[1, 2, 3, 4], help='1: edge model, 2: inpaint model, 3: edge-inpaint model, 4: joint model')

    # test mode
    parser.add_argument('--input', type=str, help='path to the input images directory or an input image')
    parser.add_argument('--edge', type=str, help='path to the edges directory or an edge file')
    parser.add_argument('--output', type=str, help='path to the output directory')
    parser.add_argument('--remove', nargs= '*' ,type=int, help='objects to remove')
    parser.add_argument('--cpu', type=str, help='machine to run segmentation model on')
    args = parser.parse_args()
    """
    #if path for checkpoint not given
    path='./checkpointsremoval'
    config_path = os.path.join(path, 'config.yml')

    # load config file
    config = Config(config_path)

   
    # test mode
    config.MODE = 2
    config.MODEL = 3
    config.OBJECTS = [15]
    config.SEG_DEVICE = 'cpu' if 'cpu' is not None else 'cuda'
    config.INPUT_SIZE = 800
    config.TEST_FLIST = 'static/client/img'

    config.TEST_EDGE_FLIST = './checkpointsremoval'
    config.RESULTS = 'static/client/img'
    config.RESULTS = 'static/client/img'

    return config


if __name__ == "__main__":
    main()
