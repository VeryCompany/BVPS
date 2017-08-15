from thespian.actors import *
import logging
import os
from bvps.torch.torch_neural_net_lutorpy import TorchNeuralNet
import thespian.troupe


@troupe(max_count=3, idle_count=3)
class TorchActor(ActorTypeDispatcher):
    def __init__(self, *args, **kw):
        fileDir = os.path.dirname(os.path.realpath(__file__))
        modelDir = os.path.join(fileDir, '..', 'models')
        openfaceModelDir = os.path.join(modelDir, 'openface')

        self.net = TorchNeuralNet(
            os.path.join(openfaceModelDir, 'nn4.small2.v1.t7'),
            imgDim=96,
            cuda=True)

    def receiveMsg_str(self, message, sender):
        logging.info("received msg {}".format(message))
