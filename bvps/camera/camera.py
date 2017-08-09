# -*- coding: utf-8 -*-
"""camera script."""
# 需要支持网络摄像头和本地USB摄像头

import logging as log
import multiprocessing
import sys, traceback
import threading
import time
import cv2
from bvps.camera.common import StatValue, clock
from thespian.actors import ActorTypeDispatcher
from bvps.camera.pre_processor import PreProcessor
from bvps.camera.detector import DetectorProcessor
from bvps.camera.trainer import TrainingProcessor
from bvps.camera.recognizer import SVMRecognizer
from bvps.common import ModelUpdateCmd
from bvps.common import CameraCmdType, TrainingCMD, CameraType
from bvps.config import cameras as cams


def Handle_exception(exc_type, exc_value, exc_traceback):
    """exception."""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    log.error(
        "Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))


# sys.excepthook = Handle_exception


class Camera(ActorTypeDispatcher):
    svm_model = None
    svm_model_updated = False
    training_started = False
    training_start_time, training_end_time = None, None
    training_uid = None

    def __init__(self, *args, **kw):
        """Init camera setting up."""
        super(Camera, self).__init__(*args, **kw)

        self.frame_queue = multiprocessing.Queue(16)  #

        self.pre_process_queue = multiprocessing.Queue(256)  # 图像预处理Queue

        self.human_detector_q = multiprocessing.Queue(256)  # 人脸和人体识别器

        self.training_dset_q = multiprocessing.Queue(
            64)  # frame queue for trainer
        self.training_model_oq = multiprocessing.Queue(
            64)  # Update old recognize model queue

        self.recognizer_in_q = multiprocessing.Queue(64)  # 识别器输入队列包括图片和模型
        self.recognizer_out_q = multiprocessing.Queue(64)  # 识别器输入队列

        Camera.user_queue = multiprocessing.Queue(64)
        self.webserver = None
        self.cct = None
        self.cameraType = None
        log.info("初始化摄像头{}".format(self))

    def receiveMsg_CameraCmd(self, cmd, sender):
        if self.webserver is not None:
            log.info(self.webserver.pid)
        # todo:异常处理！！！！！
        if CameraCmdType.START_CAPTURE == cmd.cmdType:
            if self.cct is not None and self.cct.isAlive():
                return
            self.cameraType = cmd.values["cameraType"]
            """视频采集线程"""
            log.info("摄像头 {} 接收到 START_CAPTURE 命令".format(cmd.cameraName))
            self.cameraId = cmd.cameraName
            self.cct = CameraCaptureThread(self, cmd.cameraName,
                                           cmd.values["device"], cmd)
            self.cct.setDaemon(True)
            self.cct.start()
            """监控视频Web服务器"""
            from bvps.web.server import WebServer
            log.info("启动摄像头web服务器...")
            self.webserver = WebServer(self.frame_queue, cmd.values["port"])
            self.webserver.start()
            log.info("摄像头web服务器启动完成...")

            pn = cmd.values["processNum"]  # 多进程处理进程数量
            """图像预处理启动"""
            log.info("启动摄像头[{}]图像预处理进程{}个".format(cmd.cameraName, pn))
            for p in range(0, pn, 1):
                pps = PreProcessor(self, self.pre_process_queue,
                                   self.human_detector_q)
                pps.start()
            log.info(
                "启动摄像头[{}]图像预处理进程成功！启动了[{}]个实例.".format(cmd.cameraName, pn))
            """检测器进程启动"""
            dps_num = 8
            log.info("启动摄像头[{}]图像检测器进程{}个".format(cmd.cameraName, dps_num))
            for p in range(0, dps_num, 1):
                dps = DetectorProcessor(self, self.human_detector_q,
                                        self.training_dset_q,
                                        self.recognizer_in_q)
                dps.start()
            log.info(
                "启动摄像头[{}]图像检测器成功！启动了[{}]个实例.".format(cmd.cameraName, dps_num))

            """识别器进程启动"""
            srz_num = 1
            log.info("启动摄像头[{}]图像识别器进程{}个".format(cmd.cameraName, srz_num))
            for p in range(0, srz_num, 1):
                srz = SVMRecognizer(self, self.recognizer_in_q,
                                    self.recognizer_out_q)
                srz.start()
            log.info(
                "启动摄像头[{}]图像识别器成功！启动了[{}]个实例.".format(cmd.cameraName, srz_num))
            """
            检查有新的模型输出
            training_model_oq if have update then --> recognizer_in_q
            """
            mtp = threading.Thread(
                target=self.model_process,
                args=(self.training_model_oq, self.recognizer_in_q, ),
                name="model_update_processor")
            mtp.setDaemon(True)
            mtp.start()
            if cmd.values["cameraType"] == CameraType.CAPTURE:
                """训练器进程启动"""
                log.info("启动摄像头[{}]图像训练器进程{}个".format(cmd.cameraName, 1))
                for p in range(0, 1, 1):
                    tps = TrainingProcessor(self, self.training_dset_q,
                                            self.training_model_oq)
                    tps.start()
                log.info("启动摄像头[{}]图像训练器成功！启动了[{}]个实例.".format(cmd.cameraName, 1))

            """
            检查有新的用户定位输出
            recognizer_out_q if have then --> PositionActor
            """
            from bvps.system.position_actor import PositionActor
            self.pa = self.createActor(
                PositionActor,
                targetActorRequirements=None,
                globalName="CameraPositionActor",
                sourceHash=None)
            utp = threading.Thread(
                target=self.process_user,
                args=(self.recognizer_out_q, ),
                name="user_position_sender")
            utp.setDaemon(True)
            utp.start()
            """
            队列平均性能检查
            """
            mnt = threading.Thread(
                target=self.queue_monitor, args=(), name="minitor_thread")
            mnt.setDaemon(True)
            mnt.start()
        elif CameraCmdType.STOP_CAPTURE == cmd.cmdType:
            if self.cct is not None and self.cct.isAlive():
                self.cct.stop()
                self.cct.join(timeout=10)
            self.send(sender, "camera stopped!")

    last_count_time = time.time()

    def queue_monitor(self):
        pre_queue_stat = StatValue()
        human_detector_q_stat = StatValue()
        training_dset_q_stat = StatValue()
        recognizer_in_q_stat = StatValue()
        count_times = 1
        while True:
            pre_queue_stat.update(pre_queue_stat.value +
                                  self.pre_process_queue.qsize())
            human_detector_q_stat.update(human_detector_q_stat.value +
                                         self.human_detector_q.qsize())
            training_dset_q_stat.update(training_dset_q_stat.value +
                                        self.training_dset_q.qsize())
            recognizer_in_q_stat.update(recognizer_in_q_stat.value +
                                        self.recognizer_in_q.qsize())
            if count_times > 10:
                log.info(
                    "{}预处理堆积{:0.1f},探测器堆积{:0.1f},训练器堆积{:0.1f},识别器堆积{:0.1f}".format(
                        self.cameraId, pre_queue_stat.value / count_times,
                        human_detector_q_stat.value / count_times,
                        training_dset_q_stat.value / count_times,
                        recognizer_in_q_stat.value / count_times))
                count_times = 1
                pre_queue_stat.update(0)
                human_detector_q_stat.update(0)
                training_dset_q_stat.update(0)
                recognizer_in_q_stat.update(0)
            count_times += 1
            time.sleep(1)

    def model_process(self, in_queue, out_queue):
        model = in_queue.get()
        # out_queue.put(ModelUpdateCmd(model))
        log.info("有新的识别模型，发送给定位摄像头！")
        self.send_model_to_all_camera(ModelUpdateCmd(model))
        log.info("识别模型同步完成！")

    def send_model_to_all_camera(self, model):
        for camId, params in cams.items():
            if self.cameraId != camId and params["cameraType"] == CameraType.POSITION:
                log.info("新的识别模型发送给{}".format(camId))
                cam = self.createActor(Camera, globalName=camId)
                self.send(cam, model)
                log.info("新的识别模型发送给{}完成！".format(camId))

    def receiveMsg_TrainingCMD(self, cmd, sender):
        if cmd.cctype == CameraCmdType.TRAINOR_START:
            # self.training_start_time = int(cmd.msg)
            # self.training_end_time = int(cmd.msg + 10)
            # self.training_uid = cmd.uid
            # 将开始指令发送至训练器
            self.training_dset_q.put(
                TrainingCMD(CameraCmdType.TRAINOR_START, clock(), cmd.uid))
            log.info("用户{},时间{}".format(cmd.uid, cmd.msg))
        elif cmd.cctype == CameraCmdType.TRAINOR_CAPTURE_OK:
            self.training_start_time, self.training_end_time = None, None
            self.training_uid = cmd.uid
        elif cmd.cctype == CameraCmdType.MODEL_UPDATED:
            self.svm_model = cmd.msg
            self.svm_model_updated = True

    def receiveMsg_ModelUpdateCmd(self, cmd, sender):
        log.info("{}收到新的识别模型".format(self.cameraId))
        self.recognizer_in_q.put(cmd)

    def process_user(self, uq):
        while True:
            um = uq.get()
            self.send(self.pa, um)


from multiprocessing.pool import ThreadPool
from collections import deque


class CameraCaptureThread(threading.Thread):
    """
    摄像头抓取线程类，比较初级，健壮性不足，未来需要重写
    """

    def __init__(self, camera, cameraName, cameraDevice, initCmd=None):
        threading.Thread.__init__(self)
        self._stop_event = threading.Event()
        self.camera = camera
        self.cameraName = cameraName
        self.cameraDevice = cameraDevice
        self.threadn = cv2.getNumberOfCPUs() * 4
        self.pools = {}
        self.initCmd = initCmd

    def startCapture(self):
        try:
            video = cv2.VideoCapture(self.cameraDevice)
            log.info("摄像头{}初始化参数".format(self.cameraName))
            for k, v in self.initCmd.values["video_properties"].items():
                video.set(k, v)
                log.info("video.set({},{})".format(k, v))
            forcc = self.initCmd.values[
                "fourcc"] if "fourcc" in self.initCmd.values else None
            if forcc is not None:
                video.set(cv2.CAP_PROP_FOURCC,
                          cv2.VideoWriter_fourcc(forcc[0], forcc[1], forcc[2],
                                                 forcc[3]))
            width = video.get(cv2.CAP_PROP_FRAME_WIDTH)
            height = video.get(cv2.CAP_PROP_FRAME_HEIGHT)
            codec = video.get(cv2.CAP_PROP_FOURCC)
            self.resolution = (width, height)
            log.info("摄像头fps[{}] width:{} height:{} codec:{}".format(
                video.get(cv2.CAP_PROP_FPS), width, height, codec))
            log.info("亮度:{}".format(video.get(cv2.CAP_PROP_BRIGHTNESS)))
            log.info("对比度:{}".format(video.get(cv2.CAP_PROP_CONTRAST)))
            log.info("饱和度:{}".format(video.get(cv2.CAP_PROP_SATURATION)))
            log.info("色调:{}".format(video.get(cv2.CAP_PROP_HUE)))
            log.info("图像增益:{}".format(video.get(cv2.CAP_PROP_GAIN)))
            log.info("曝光:{}".format(video.get(cv2.CAP_PROP_EXPOSURE)))
            log.info("ISO:{}".format(video.get(cv2.CAP_PROP_ISO_SPEED)))
            log.info("RGB?:{}".format(video.get(cv2.CAP_PROP_CONVERT_RGB)))
            """
            # 处理方式 1
            frame_interval = StatValue()
            last_frame_time = clock()
            num = 10
            while True:
                try:
                    if self.stopped():
                        break
                    if video.grab():
                        ret, frame = video.retrieve()
                        frame_time = time.time()
                        if num % 50 == 0:
                            log.debug("读取摄像头{}frame{}".format(
                                self.cameraName, "成功" if ret else "失败！"))
                        t = clock()
                        frame_interval.update(t - last_frame_time)
                        if num % 50 == 0:
                            log.debug("摄像头{}.当前fps:{}".format(
                                self.cameraName,
                                int(1000 / (frame_interval.value * 1000))))
                        if ret:
                            if not self.camera.pre_process_queue.full():
                                self.camera.pre_process_queue.put_nowait(
                                    (frame, t, frame_time))
                            if not self.camera.frame_queue.full():
                                self.camera.frame_queue.put_nowait((frame, t,
                                                                   frame_time))
                        last_frame_time = t
                    num += 1
                except Exception, e:
                    log.info(e.message)
            """
            """处理方式2"""

            def process_frame(frame, t0, fts):
                if not self.camera.pre_process_queue.full():
                    self.camera.pre_process_queue.put((frame, t, fts))
                if not self.camera.frame_queue.full():
                    self.camera.frame_queue.put((frame, t, fts))
                return frame, t0, fts

            threadn = cv2.getNumberOfCPUs()
            pool = ThreadPool(processes=threadn)
            pending = deque()

            latency = StatValue()
            frame_interval = StatValue()
            last_frame_time = clock()
            while True:
                while len(pending) > 0 and pending[0].ready():
                    frame, t0, fts = pending.popleft().get()
                    latency.update(clock() - t0)
                if len(pending) < threadn:
                    frame_time = time.time()
                    ret, frame = video.read()
                    t = clock()
                    frame_interval.update(t - last_frame_time)
                    last_frame_time = t
                    if ret:
                        task = pool.apply_async(process_frame, (frame.copy(),
                                                                t, frame_time))
                        pending.append(task)
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            log.error(
                traceback.format_exception(exc_type, exc_value, exc_traceback))

    def run(self):
        self.startCapture()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()


# 摄像头命令类型定义
