# -*- coding: utf-8 -*-
from thespian.actors import *
class VideoRecord(ActorTypeDispatcher):
    def __init__(self, *args, **kw):
        super(VideoRecord, self).__init__(*args, **kw)
    def receiveMsg_tuple(self, message, sender):
        pass
    def receiveMsg_Image(self, message, sender):
        pass
