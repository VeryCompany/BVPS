from thespian.actors import *
import logging
import os
from bvps.torch.torch_neural_net_lutorpy import TorchNeuralNet
from thespian.troupe import troupe
from thespian.actors import requireCapability

# @troupe(max_count=10, idle_count=10)


@requireCapability('torch')
class TorchActor(Actor):
    def __init__(self, *args, **kw):
        log.info("ready to init torch actor.....")
        fileDir = os.path.dirname(os.path.realpath(__file__))
        modelDir = os.path.join(fileDir, '..', 'models')
        openfaceModelDir = os.path.join(modelDir, 'openface')
        self.net = TorchNeuralNet(
            os.path.join(openfaceModelDir, 'nn4.small2.v1.t7'),
            imgDim=96,
            cuda=True)

    def receiveMsg_tuple(self, message, sender):
        cameraId, human, t0, sec, center, size = message
        px, py = center
        rep = self.net.forward(human)
        self.send(sender, (cameraId, rep[0], center, t0, sec))
        log.info("received identity request from {}, image.shape:{}".format(
            cameraId, human.shape))

    def receiveMessage(self, message, sender):
        pass
