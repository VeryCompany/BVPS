from thespian.actors import *
from thespian.actors import ActorTypeDispatcher
import logging
import os
from bvps.torch.torch_neural_net_lutorpy import TorchNeuralNet
from thespian.troupe import troupe
from thespian.actors import requireCapability
import _thread


@troupe(max_count=10, idle_count=10)
class TorchActor(ActorTypeDispatcher):
    def __init__(self, *args, **kw):
        log.info("ready to init torch actor.....")
        _thread.start_new_thread(_init_torch, ())

    def receiveMsg_tuple(self, message, sender):
        cameraId, human, t0, sec, center, size = message
        px, py = center
        log.info("received identity request from {}, image.shape:{}".format(
            cameraId, human.shape))
        rep = self.net.forward(human)
        self.send(sender, (cameraId, rep[0], center, t0, sec))

    def _init_torch(self):
        log.info("ready to lunch torch neura net....")
        fileDir = os.path.dirname(os.path.realpath(__file__))
        modelDir = os.path.join(fileDir, '..', 'models')
        openfaceModelDir = os.path.join(modelDir, 'openface')
        self.net = TorchNeuralNet(
            os.path.join(openfaceModelDir, 'nn4.small2.v1.t7'),
            imgDim=96,
            cuda=True)
        log.info("lunch torch neura net ok ....")
