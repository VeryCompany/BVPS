# -*- coding: utf-8 -*-
import logging as log
import os
import multiprocessing.Process
import numpy as np
import openface

fileDir = os.path.dirname(os.path.realpath(__file__))
modelDir = os.path.join(fileDir, '..', 'models')
openfaceModelDir = os.path.join(modelDir, 'openface')
net = openface.TorchNeuralNet(
    os.path.join(openfaceModelDir, 'nn4.small2.v1.t7'), imgDim=96, cuda=True)

class SVMRecognizer(multiprocessing.Process):

    def __init__(self, svm, in_queue, out_queue):
        multiprocessing.Process.__init__(self)
        SVMRecognizer.in_queue = in_queue
        SVMRecognizer.out_queue = out_queue


    def whoru(self,human):
        log.info(self.svm)
        if self.svm is None:
            return None
        face = human[0][0]
        X = face.flatten()
        # 需要图片扁平化处理
        rep = net.forward(X)
        identity = self.svm.predict(rep)[0]
        return identity
