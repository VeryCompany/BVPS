# -*- coding: utf-8 -*-
"""camera script."""
import logging as log
import multiprocessing
from bvps.camera.common import clock, StatValue
import cv2


class PreProcessor(multiprocessing.Process):
    def __init__(self, camera, frame_in, frame_out):
        multiprocessing.Process.__init__(self, name="video_frame_PreProcessor")
        PreProcessor.frame_in = frame_in
        PreProcessor.frame_out = frame_out
        self.camera = camera
        self.frame_interval = StatValue()
        self.last_frame_time = clock()
        self.latency = StatValue()
    def run(self):
        from bvps.config import cameras as ca
        scale = ca[self.camera.cameraId]["scale"]
        while True:
            frame, t0, ts = PreProcessor.frame_in.get()
            h, w, d = frame.shape

            if scale is not None and scale != 1:
                frame = cv2.resize(frame, (int(w * scale), int(h * scale)))
            PreProcessor.frame_out.put((frame, t0, ts))
            log.debug("{},latency:{:0.1f}ms,process time:{:0.1f}ms".format(self.camera.cameraId,self.latency.value * 1000, self.frame_interval.value*1000))
            t = clock()
            self.latency.update(t-t0)
            self.frame_interval.update(t-self.last_frame_time)
            self.last_frame_time = t
