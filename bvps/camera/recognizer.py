# -*- coding: utf-8 -*-
import os
import numpy as np
import openface
import logging as log



fileDir = os.path.dirname(os.path.realpath(__file__))
modelDir = os.path.join(fileDir, '..', 'models')
openfaceModelDir = os.path.join(modelDir, 'openface')
net = openface.TorchNeuralNet(
    os.path.join(openfaceModelDir, 'nn4.small2.v1.t7'), imgDim=96, cuda=False)

recognizers = []
class Face:

    def __init__(self, rep, identity):
        self.rep = rep
        self.identity = identity

    def __repr__(self):
        return "{{id: {}, rep[0:5]: {}}}".format(
            str(self.identity),
            self.rep[0:5]
        )
class OpenFaceRecognizer(object):
    def __init__(self,svm):
        self.svm = svm
    def whoru(self,human,t0):
        face = human[1][0]
        rep = net.forward(face)
        identity = self.svm.predict(rep)[0]
        return identity
