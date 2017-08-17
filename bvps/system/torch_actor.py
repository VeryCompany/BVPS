from thespian.actors import *
import logging
import os
from bvps.torch.torch_neural_net_lutorpy import TorchNeuralNet
from thespian.troupe import troupe
from thespian.actors import requireCapability


@requireCapability('torch')
@troupe(max_count=10, idle_count=10)
class TorchActor(ActorTypeDispatcher):
    def __init__(self, *args, **kw):
        fileDir = os.path.dirname(os.path.realpath(__file__))
        modelDir = os.path.join(fileDir, '..', 'models')
        openfaceModelDir = os.path.join(modelDir, 'openface')
        self.net = TorchNeuralNet(
            os.path.join(openfaceModelDir, 'nn4.small2.v1.t7'),
            imgDim=96,
            cuda=True)

    def receiveMsg_tuple(self, message, sender):
        camId, image = message

        rep = self.net.forward(image)
        self.send(sender, rep)
        log.info("received identity request from {}, image.shape:{}".format(
            camId, image.shape))
