# -*- coding: utf-8 -*-
from enum import Enum
import os
from bvps.dlib.align_dlib import AlignDlib
from bvps.torch.torch_neural_net import TorchNeuralNet


fileDir = os.path.dirname(os.path.realpath(__file__))
modelDir = os.path.join(fileDir, 'models')
dlibModelDir = os.path.join(modelDir, 'dlib')
harrsDir = os.path.join(fileDir, 'haars')
openfaceModelDir = os.path.join(modelDir, 'openface')
mtnnDir = os.path.join(fileDir, "..", "model")
align = AlignDlib(
    os.path.join(dlibModelDir, "shape_predictor_68_face_landmarks.dat"))

net = TorchNeuralNet(
     os.path.join(openfaceModelDir, 'nn4.small2.v1.t7'), imgDim=96, cuda=True)


class CameraCmdType(Enum):
    START_CAPTURE = 1
    STOP_CAPTURE = 2
    RESTART_CAPTURE = 3
    START_CAPTURE_FOR_COLLECTION = 4
    TRAINOR_INIT = 5
    TRAINOR_START = 6
    TRAINOR_END = 7
    PERSON_LEAVE = 8
    TRAINOR_CAPTURE_OK = 9
    MODEL_UPDATED = 10


class CameraType(Enum):
    CAPTURE = 1
    POSITION = 2
    BOTH_CAPTURE_POSITION = 3


class TrainingCMD(object):
    def __init__(self, cctype, msg, uid=None):
        self.cctype = cctype
        self.msg = msg
        self.uid = uid


# 摄像头命令定义
class CameraCmd(object):
    def __init__(self,
                 cmdType=CameraCmdType.START_CAPTURE,
                 cameraName=None,
                 values={}):
        self.cmdType = cmdType
        self.values = values
        self.cameraName = cameraName


class ModelUpdateCmd(object):
    u"""如果模型发生变更，通知识别器."""

    def __init__(self, model):
        u"""构造函数."""
        self.model = model
