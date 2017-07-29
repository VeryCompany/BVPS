# -*- coding: utf-8 -*-
"""camera script."""
import logging as log
import multiprocessing
from bvps.config import cameras as ca
import cv2


class PreProcessor(multiprocessing.Process):
    def __init__(self, camera, frame_in, frame_out):
        multiprocessing.Process.__init__(self, name="video_frame_PreProcessor")
        PreProcessor.frame_in = frame_in
        PreProcessor.frame_out = frame_out
        self.camera = camera

    def run(self):
        scale = ca[self.camera.cameraId]["scale"]
        while True:
            frame, t0, ts = PreProcessor.frame_in.get()
            h, w, d = frame.shape

            if scale is not None and scale != 1:
                frame = cv2.resize(frame, (int(w * scale), int(h * scale)))
            PreProcessor.out_queue.put(frame)
