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
from bvps.torch.torch_actor import TorchActor


class SVMRecognizer(multiprocessing.Process):
    def __init__(self, camera, net, in_queue, out_queue):
        multiprocessing.Process.__init__(self, name="video_human_recognizer")
        SVMRecognizer.in_queue = in_queue
        SVMRecognizer.out_queue = out_queue
        self.camera = camera
        self.model = None
        self.frame_interval = StatValue()
        self.last_frame_time = clock()
        self.latency = StatValue()
        self.net = net

    def whoru(self, human):
        face = human
        # rep = self.actor_system.ask(self.net, (self.camera.cameraId, face), 5)
        if self.net is not None:
            rep = self.net.forward(face)
        identity = None
        if self.model is not None:
            identity = self.model.predict(rep)[0]
        return identity

    def run(self):

        while True:
            try:
                msg = SVMRecognizer.in_queue.get()
                if isinstance(msg, ModelUpdateCmd):
                    self.model = msg.model
                    continue
                human, t0, sec, center, size = msg
                px, py = center
                uid = self.whoru(human)
                if uid is not None:
                    # 用户uid出现在图片坐标(px,py),精确时间t0,秒时间sec
                    log.info(
                        "user:{},px:{},py:{},sec:{}".format(uid, px, py, sec))
                    SVMRecognizer.out_queue.put((self.camera.cameraId, uid,
                                                 (px, py), t0, sec))
                t = clock()
                self.latency.update(t - t0)
                self.frame_interval.update(t - self.last_frame_time)
                self.last_frame_time = t
            except Exception as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                log.error(
                    traceback.format_exception(exc_type, exc_value,
                                               exc_traceback))
