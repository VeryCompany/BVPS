# -*- coding: utf-8 -*-
"""camera script."""
import logging as log
import multiprocessing
from bvps.camera.common import clock, StatValue
import cv2
from multiprocessing.pool import ThreadPool
from collections import deque


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
        threadn = cv2.getNumberOfCPUs()
        pool = ThreadPool(processes=threadn * 2)
        pending = deque()
        while True:
            while len(pending) > 0 and pending[0].ready():
                frame, t0, ts = pending.popleft().get()
                #if not PreProcessor.frame_out.full():
                PreProcessor.frame_out.put((frame, t0, ts))
            if len(pending) < threadn:
                frame, t0, ts = PreProcessor.frame_in.get()
                task = pool.apply_async(self.resize_frame, (frame, scale, t0,
                                                            ts))
                pending.append(task)
                t = clock()
                self.latency.update(t - t0)
                self.frame_interval.update(t - self.last_frame_time)
                self.last_frame_time = t
            log.debug("{},latency:{:0.1f}ms,process time:{:0.1f}ms".format(
                self.camera.cameraId, self.latency.value * 1000,
                self.frame_interval.value * 1000))

    def resize_frame(self, frame, scale, t0, ts):
        h, w, d = frame.shape
        if scale == 1:
            return (frame, t0, ts)
        f = cv2.resize(frame, (int(w * scale), int(h * scale)))
        return (f, t0, ts)
