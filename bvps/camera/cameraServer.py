# -*- coding: utf-8 -*-
import logging as log
import multiprocessing
import cv2

from bvps.camera.common import clock, StatValue
from bvps.camera.detectorthread import HumanDetector as detector
from bvps.camera.recognizer import OpenFaceRecognizer as recognizer
from multiprocessing.dummy import Pool as ThreadPool


class CameraServer(multiprocessing.Process):
    def __init__(self, queue, cmd, user_queue, cct):
        multiprocessing.Process.__init__(self)
        CameraServer.queue = queue

        CameraServer.trainor_queue = multiprocessing.Queue(64)
        CameraServer.svm_queue = multiprocessing.Queue(64)

        trainoingserv=TrainingServer(CameraServer.trainor_queue, CameraServer.svm_queue)
        trainoingserv.start()

        self.cmd = cmd
        from bvps.camera.camera import Camera
        self.user_queue = user_queue
        self.cct = cct
        self.detector = detector()
        self.recognizer = recognizer(None)
        self.threadn = cv2.getNumberOfCPUs()
        self.pools = {}
        # from bvps.system.position_actor import PositionActor
        # self.position = camera.createActor(
        #     PositionActor,
        #     targetActorRequirements=None,
        #     globalName="CameraPositionActor",
        #     sourceHash=None)
        # from bvps.camera.trainer import HumanModelTrainer
        # self.trainor = camera.createActor(
        #     HumanModelTrainer,
        #     targetActorRequirements=None,
        #     globalName="HumanModelTrainer",
        #     sourceHash=None)
        # camera.send(self.trainor,"创建培训期")


    def run(self):
        latency = StatValue()
        while True:
            frame, t0, secs, start, end, uid = CameraServer.queue.get()
            self.process_frame(frame, t0, secs, start, end, uid)
            t = clock()
            latency.update(t - t0)
            log.debug("摄像头[{}]进程{}处理数据，处理耗时{:0.1f}ms...".format(
                self.cmd.cameraName, self.pid, latency.value * 1000))

    def process_frame(self, frame, t0, secs, start, end, uid):
        if self.camera.svm_model_updated:
            self.recognizer.svm = self.camera.svm_model
            self.camera.svm_model_updated = False
        humans = self.detector.detect_humans(self.cmd.cameraName, frame, t0,
                                             secs)
        #if self.camera. startTrainning():
        """
        sending humans to trainning actors
        通过通道的人，需要开始和结束时间，基准时间t0
        """
        #log.info("探测到{}个人".format(len(humans)))
        if len(humans) > 0:
            log.info("{}---{}--{}".format(secs, start, end))
            if (start is not None and secs > start) and (end is None
                                                         or secs < end):
                for human in humans:
                    # log.info(self.trainor)
                    CameraServer.trainor_queue.put_nowait((human, uid))
            if CameraServer.svm_queue.qsize() > 0:
                self.recognizer.svm = CameraServer.svm_queue.get()

            users = self.recognizeParallel(self.process_recognize, humans)

    def recognizeParallel(self, method, humans):
        """多线程并行运算，提高运算速度"""
        kt = clock()
        pool = ThreadPool(processes=self.threadn)
        self.pools[kt] = pool
        results = pool.map_async(method, humans)
        pool.close()
        pool.join()
        pool.terminate()
        self.pools.pop(kt, None)
        return results

    def process_recognize(self, human):
        """识别检测到的人体图片，返回人对应的用户Id"""
        #log.debug("开始识别人！")

        try:
            t0 = human[2]
            secs = human[3]
            uid = self.recognizer.whoru(human)
            #if self.recognizer.svm is not None else None
            log.info("摄像头{}识别用户id：{},x:{},y:{}".format(
                self.cmd.cameraName, uid, human[0][1], human[0][2]))
            if uid is not None:
                msg = (self.cmd.cameraName, uid, human[0][1], human[0][2],
                       human[0][0], self.cct.resolution, 0, int(secs))
                self.user_queue.put_nowait(msg)
            return human, uid
        except Exception, e:
            log.info(e.message)
            return human, None

# from bvps.config import training_config as tc

tc = {
    "cap_nums":30
}

from sklearn.grid_search import GridSearchCV
from sklearn.svm import SVC
# from bvps.config import svm_param_grid as spg

spg = [
    {'C': [1, 10, 100, 1000],
     'kernel': ['linear']},
    {'C': [1, 10, 100, 1000],
     'gamma': [0.001, 0.0001],
     'kernel': ['rbf']}
]

import copy
class TrainingServer(multiprocessing.Process):
    human_map = {}

    def __init__(self, in_queue, out_queue):
        multiprocessing.Process.__init__(self)
        self.in_queue = in_queue
        self.out_queue = out_queue
    def run(self):
        global tc
        last_uid = None
        while True:
            """
            接收N张照片，如果接收到足够数量的样本，返回消息
            """
            message = self.in_queue.get()
            human = message[0][0]
            uid = message[1]
            t0 = message[0][2]
            if uid == last_uid :
                continue
            if len(self.human_map[uid]) < tc["cap_nums"]:
                self.human_map[uid].append(human)

            log.info("接收到用户{}的样本图片，样本数量{}".format(uid, len(self.human_map[uid])))
            if len(self.human_map[uid]) >= tc["cap_nums"]:

                self.train()
                self.out_queue.put_nowait(self.svm)
                last_uid = uid
                # self.send(sender,
                #           TrainingCMD(CameraCmdType.TRAINOR_CAPTURE_OK, "ok", uid))
                # self.train()
                # self.send(sender,
                #           TrainingCMD(CameraCmdType.MODEL_UPDATED, self.svm))
            # 训练不应该在这里！

    def train(self):
        global spg
        uids, images = [], []
        hums = copy.deepcopy(self.human_map)
        for uid, imgs in hums:
            if len(imgs) < tc["cap_nums"]:
                continue
            images.extend(imgs)
            uids.extend([uid for x in range(len(imgs))])
        self.svm = GridSearchCV(SVC(C=1), spg, cv=5).fit(images, uids)
        return self.svm
