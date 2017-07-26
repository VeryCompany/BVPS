# -*- coding: utf-8 -*-
from thespian.actors import ActorTypeDispatcher

class CoreActor(ActorTypeDispatcher):

    def __init__(self, *args, **kw):
        super(CoreActor, self).__init__(*args, **kw)
        self.userCount = 0
        self.userList = []
        self.userapphistory = {}
        self.usercamerahistory = {}
        self.maxCount = 10

    def receiveMsg_UserEvent(self, message, sender):
        userId = message.userId
        event = message.event
        if event == "in":
            if userId not in self.userList:
                self.userList.append(userId)
                self.userCount += 1
        elif event == "out":
            if userId in self.userList:
                self.userList.remove(userId)
                self.userCount -= 1

    def receiveMsg_UserLoc(self, message, sender):
        userId = message.userId
        loc = message.loc
        device = message.device
        time = message.time
        userList = None
        if device == "camera":
            if time in self.usercamerahistory:
                userList = self.usercamerahistory[time]
            if userList is None:
                userList = []
                userList.append({userId:loc})
                self.usercamerahistory[time]=userList
            else:
                userList.append({userId:loc})
                self.usercamerahistory[time] = userList

            print "="*5,self.usercamerahistory

            if len(self.usercamerahistory) > self.maxCount:
                times = sorted(self.usercamerahistory.keys(), cmp=lambda time1, time2: cmp(time2, time1))
                for locTime in times[self.maxCount:]:
                    self.usercamerahistory.pop(locTime)
            print "-"*5,self.usercamerahistory
        elif device == "app":
            if time in self.userapphistory:
                userList = self.userapphistory[time]
            if userList is None:
                userList = []
                userList.append({userId: loc})
                self.userapphistory[time] = userList
            else:
                userList.append({userId: loc})
                self.userapphistory[time] = userList

            print "=" * 7, self.userapphistory
            if len(self.userapphistory) > self.maxCount:
                times = sorted(self.userapphistory.keys(), cmp=lambda time1,time2 : cmp(time2, time1))
                for locTime in times[self.maxCount:]:
                    self.userapphistory.pop(locTime)
            print "-" * 7, self.userapphistory

    def receiveMsg_FindUser(self, message, sender):
        self.send(sender, (self.userList, self.userCount))

class UserEvent():

    def __init__(self, userId, event):
        self.userId = userId
        self.event = event

class UserLoc():

    def __init__(self, userId, time, userloc, device="camera"):
        self.userId = userId
        self.time = time
        self.loc = userloc
        self.device = device

class FindUser():

    def __init__(self):
        pass