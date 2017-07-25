# -*- coding: utf-8 -*-
from thespian.actors import ActorTypeDispatcher

class CoreActor(ActorTypeDispatcher):

    def __init__(self, *args, **kw):
        super(CoreActor, self).__init__(*args, **kw)
        self.userCount = 0
        self.userList = []
        self.userapphistory = {}
        self.usercamerahistory = {}

    def receiveMsg_UserCome(self, message, sender):
        pass

    def receiveMsg_UserLeave(self, message, sender):
        pass

    def receiveMsg_UserCameraLoc(self, message, sender):
        pass

    def receiveMsg_UserAppLoc(self, message, sender):
        pass

    def receiveMsg_FindUser(self, message, sender):
        pass
