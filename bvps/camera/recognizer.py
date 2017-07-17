# -*- coding: utf-8 -*-
from thespian.actors import *
from thespian.troupe import troupe
#识别人
@troupe(max_count=2,idle_count=2)
class HumanRecognizer(ActorTypeDispatcher):
    def __init__(self, *args, **kw):
        super(HumanRecognizer, self).__init__(*args, **kw)
    def receiveMsg_list(self, message, sender):
        print "received person image"
    def receiveMsg_Image(self, message, sender):
        pass
