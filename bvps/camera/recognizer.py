# -*- coding: utf-8 -*-

import logging as log
import multiprocessing
import os
import sys
import traceback
from thespian.actors import ActorSystem
from bvps.logger import logcfg
from bvps.camera.camera import StatValue, clock
from bvps.common import ModelUpdateCmd
from bvps.torch.torch_neural_net_lutorpy import TorchNeuralNet
from bvps.system.torch_actor import TorchActor


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
        self.ta = None
        log.info("初始化识别器！")

    # def whoru(self, human):
    #     face = human
    #     if self.net is not None:
    #         rep = self.net.forward(face)
    #     identity = None
    #     if self.model is not None:
    #         identity = self.model.predict(rep)[0]
    #     return identity

    def run(self):
        # try:
        # fileDir = os.path.dirname(os.path.realpath(__file__))
        # modelDir = os.path.join(fileDir, '..', 'models')
        # openfaceModelDir = os.path.join(modelDir, 'openface')
        # self.net = TorchNeuralNet(
        #     os.path.join(openfaceModelDir, 'nn4.small2.v1.t7'),
        #     imgDim=96,
        #     cuda=True)

        self.ta = self.camera.createActor(
            TorchActor,
            globalName="TorchActor")
        log.info("create torch.TorchActor ok.....")

        while True:
            try:
                msg = SVMRecognizer.in_queue.get()
                
                if isinstance(msg, ModelUpdateCmd):
                    self.model = msg.model
                    continue
                human, t0, sec, center, size = msg
                self.camera.send(self.ta, (self.camera.cameraId, human, t0, sec,
                                           center, size))
                # uid = self.whoru(human)
                # if uid is not None:
                # 用户uid出现在图片坐标(px,py),精确时间t0,秒时间sec
                # log.info(
                #     "user:{},px:{},py:{},sec:{}".format(uid, px, py, sec))
                # SVMRecognizer.out_queue.put((self.camera.cameraId, uid,
                #                              (px, py), t0, sec))
                t = clock()
                self.latency.update(t - t0)
                self.frame_interval.update(t - self.last_frame_time)
                self.last_frame_time = t
            except Exception as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                log.error(
                    traceback.format_exception(exc_type, exc_value,
                                               exc_traceback))
        # except Exception as e:
        #     exc_type, exc_value, exc_traceback = sys.exc_info()
        #     log.error(
        #         traceback.format_exception(exc_type, exc_value, exc_traceback))
