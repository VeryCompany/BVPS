# -*- coding: utf-8 -*-
from thespian.actors import *
from thespian.troupe import troupe
#训练模型
@troupe(max_count=2,idle_count=2)
class HumanModelTrainer(ActorTypeDispatcher):
    def __init__(self, *args, **kw):
        super(HumanModelTrainer, self).__init__(*args, **kw)
    def receiveMsg_CMD(self, message, sender):
        pass
    def receiveMsg_Image(self, message, sender):
        pass