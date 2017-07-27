# -*- coding: utf-8 -*-
from thespian.actors import *
from thespian.troupe import troupe
import logging as log

from sklearn.decomposition import PCA
from sklearn.grid_search import GridSearchCV
from sklearn.manifold import TSNE
from sklearn.svm import SVC
from bvps.camera.camera import Camera, CameraCmdType, CameraCmd, TrainingCMD, CameraType
from bvps.config import training_config as tc
from bvps.config import svm_param_grid as spg
import copy


#训练模型
#@troupe(max_count=10,idle_count=5)
class HumanModelTrainer(ActorTypeDispatcher):
    human_map = {}

    def __init__(self, *args, **kw):
        super(HumanModelTrainer, self).__init__(*args, **kw)

    def receiveMsg_CMD(self, message, sender):
        pass

    def receiveMsg_TrainingCMD(self, message, sender):
        """
        开始训练模型
        离店删除图片数据集
        """
        if message.cctype == CameraCmdType.TRAINOR_END:
            uid = message.uid
            msg = message.msg
            self.train()
        elif message.cctype == CameraCmdType.PERSON_LEAVE:
            human_map.pop(message.uid)
            self.human_map_updated = True

    def receiveMsg_str(self, message, sender):
        log.info("训练器收到消息:[{}]".format(message))

    def receiveMsg_tuple(self, message, sender):
        """
        接收N张照片，如果接收到足够数量的样本，返回消息
        """
        human = message[0][0]
        uid = message[1]
        t0 = message[0][2]
        if len(human_map[uid]) < tc["cap_nums"]:
            human_map[uid].append(human)

        log.info("接收到用户{}的样本图片，样本数量{}".format(uid, len(human_map[uid])))
        if len(human_map[uid]) >= tc["cap_nums"]:
            self.send(sender,
                      TrainingCMD(CameraCmdType.TRAINOR_CAPTURE_OK, "ok", uid))
            self.train()
            self.send(sender,
                      TrainingCMD(CameraCmdType.MODEL_UPDATED, self.svm))

    def train(self):
        uids, images = [], []
        hums = copy.deepcopy(self.human_map)
        for uid, imgs in hums:
            if len(imgs) < tc["cap_nums"]:
                continue
            images.extend(imgs)
            uids.extend([uid for x in range(len(imgs))])
        self.svm = GridSearchCV(SVC(C=1), spg, cv=5).fit(images, uids)
        return self.svm
