# -*- coding: utf-8 -*-
import logging as log
import multiprocessing
import os

import numpy as np
import openface
from bvps.camera.camera import clock, StatValue
from bvps.common import ModelUpdateCmd
from sklearn.svm import SVC

fileDir = os.path.dirname(os.path.realpath(__file__))
modelDir = os.path.join(fileDir, '..', 'models')
openfaceModelDir = os.path.join(modelDir, 'openface')
net = openface.TorchNeuralNet(
    os.path.join(openfaceModelDir, 'nn4.small2.v1.t7'), imgDim=96, cuda=True)


class SVMRecognizer(multiprocessing.Process):
    def __init__(self, camera, in_queue, out_queue):
        multiprocessing.Process.__init__(self, name="video_human_recognizer")
        SVMRecognizer.in_queue = in_queue
        SVMRecognizer.out_queue = out_queue
        self.camera = camera
        self.model = None
        self.frame_interval = StatValue()
        self.last_frame_time = clock()
        self.latency = StatValue()

    def whoru(self, human):
        if self.model is None:
            return None
        face = human[0][0]
        X = face.flatten()  # 需要图片扁平化处理
        rep = net.forward(X)
        identity = self.svm.predict(rep)[0]
        return identity

    def run(self):
        while True:
            msg = SVMRecognizer.in_queue.get()
            if msg.__class__ == ModelUpdateCmd.__class__:
                self.model = msg.model
                continue
            frame, t0, sec = msg
            human, px, py = frame
            uid = self.whoru(human)
            if uid is not None:
                # 用户uid出现在图片坐标(px,py),精确时间t0,秒时间sec
                SVMRecognizer.out_queue.put((uid, (px, py), t0, sec))
            log.info(
                "recognizer_{},latency:{:0.1f}ms,process time:{:0.1f} ms".
                format(self.camera.cameraId, self.latency.value * 1000,
                       self.frame_interval.value * 1000))
            t = clock()
            self.latency.update(t - t0)
            self.frame_interval.update(t - self.last_frame_time)
            self.last_frame_time = t
