# -*- coding: utf-8 -*-
from enum import Enum


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