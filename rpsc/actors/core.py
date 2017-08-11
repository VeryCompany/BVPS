# -*- coding: utf-8 -*-
from thespian.actors import ActorTypeDispatcher
from rpsc.utils.fpLocalize import RoomClassifier
import rpsc.config as rack_config
import pickle
import numpy as np


class CoreActor(ActorTypeDispatcher):
    def __init__(self):
        super(CoreActor, self).__init__()
        self.userCount = 0
        self.userList = list()
        self.userAppHistory = dict()
        self.userCameraHistory = dict()
        self.maxCount = 15
        self.clf = RoomClassifier()

        self.rssis = [[-100] * 5, [-100] * 5, [-99] * 5, [-99] * 5, [-99] * 5, [-99] * 5]
        self.labels = [0, 0, 0, 0, 0, -1]

        with open("./rpsc/datas/traindatas", 'rb') as infile:
            data = pickle.load(infile)
            self.rssis = data["fingerprints"]
            self.labels = data["label"]
        print(self.labels)
        self.clf.fit(self.rssis, self.labels)

    def receiveMsg_UserEvent(self, message, sender):
        user_id = message.userId
        event = message.event
        print("userEvent:", sender)
        if event == "in":
            if user_id not in self.userList:
                self.userList.append(user_id)
                self.userCount += 1
        elif event == "out":
            if user_id in self.userList:
                self.userList.remove(user_id)
                self.userCount -= 1
        print(self.userList)

    def receiveMsg_UserLoc(self, message, sender):

        user_id = message.userId
        loc = message.loc
        device = message.device
        rssi_time = message.rssiTime
        user_time_dict = None

        if device == "camera":
            if rssi_time in self.userCameraHistory:
                user_time_dict = self.userCameraHistory[rssi_time]
            if user_time_dict is None:
                user_time_dict = dict()
                user_time_dict[user_id] = [loc]
                self.userCameraHistory[rssi_time] = user_time_dict
            else:
                if user_id in user_time_dict:
                    loc_list = user_time_dict[user_id]
                    loc_list.append(loc)
                    user_time_dict[user_id] = loc_list
                else:
                    user_loc_list = list()
                    user_loc_list.append(loc)
                    user_time_dict[user_id] = user_loc_list
                self.userCameraHistory[rssi_time] = user_time_dict

            print("=" * 5, self.userCameraHistory, sender)

            if len(self.userCameraHistory) > self.maxCount:
                times = sorted(self.userCameraHistory.keys())
                for locTime in times[self.maxCount:]:
                    self.userCameraHistory.pop(locTime)
            print("-" * 5, self.userCameraHistory)

        elif device == "app":
            if rssi_time in self.userAppHistory:
                user_time_dict = self.userAppHistory[rssi_time]
            if user_time_dict is None:
                user_time_dict = dict()
                user_time_dict[user_id] = [loc]
                self.userAppHistory[rssi_time] = user_time_dict
            else:
                if user_id in user_time_dict:
                    loc_list = user_time_dict[user_id]
                    loc_list.append(loc)
                    user_time_dict[user_id] = loc_list
                else:
                    user_loc_list = list()
                    user_loc_list.append(loc)
                    user_time_dict[user_id] = user_loc_list
                self.userAppHistory[rssi_time] = user_time_dict

            # print("=" * 7, len(self.userAppHistory), self.userAppHistory)
            if len(self.userAppHistory) > self.maxCount:
                times = sorted(self.userAppHistory.keys())
                for locTime in times[self.maxCount:]:
                    self.userAppHistory.pop(locTime)
            print("-" * 7, len(self.userAppHistory))

    def receiveMsg_FindUser(self, message, sender):
        rack_id = message.rackId
        change_time = message.changeTime
        rack_locs = None

        if len(self.userList) == 1:
            self.send(sender, (self.userList, len(self.userList)))
        else:
            users = list()
            if rack_id is not None:
                for rack_info in rack_config.rack_loc:
                    if str(rack_id) == rack_info["rackId"]:
                        # print rackId, rackInfo["beaconLoc"]
                        rack_locs = rack_info["beaconLoc"]
                        break

            if change_time in self.userAppHistory:
                users.extend(self.getUsers(change_time, rack_id, rack_locs))

            if len(users) == 0:
                per_time = change_time - 1
                if per_time in self.userAppHistory:
                    users.extend(self.getUsers(per_time, rack_id, rack_locs))

                if len(users) == 0:
                    per_time1 = per_time - 1
                    if per_time1 in self.userAppHistory:
                        users.extend(self.getUsers(per_time1, rack_id, rack_locs))

            if len(users) == 0:
                print("not user found !!!!! warning ....... ")
                self.send(sender, (self.userList, len(self.userList)))
            else:
                self.send(sender, (users, len(users)))

    def receiveMsg_FindUserLoc(self, message, sender):
        user_id = message.userId
        rssi_time = message.rssiTime
        rssis = message.rssis
        # loc = self.clf.classifier.predict(self.clf.dimred.transform(rssis))
        loc = self.clf.classifier.predict(np.array(rssis).reshape((1, -1)))
        print(user_id, rssi_time, loc, sender)
        # dimred = Isomap(n_neighbors=5, n_components=2, n_jobs=4, eigen_solver="dense")
        # dimred.fit_transform(self.rssis, self.lables)
        # for xx in range(5):
        #     xy = dimred.transform(X)
        #     print xy

    def receiveMsg_TrainRssis(self, message, sender):
        # self.send(sender, (self.userList, self.userCount))
        train_id = message.trainId
        rssis = message.rssis

        beacons = rack_config.beaconList

        transform_rssis = []
        for beacon in beacons:
            if beacon in rssis:
                beacon_val = rssis[beacon]
                transform_rssis.append(beacon_val)

        if len(transform_rssis) == len(beacons):
            self.labels.append(train_id)
            self.rssis.append(transform_rssis)

            if len(self.rssis) % 20 == 0:
                with open("./rpsc/datas/traindatas", 'wb') as outfile:
                    pickle.dump({
                        'fingerprints': self.rssis,
                        'label': self.labels
                    }, outfile)
                print("save train datas ....... ", sender)
                self.clf.fit(self.rssis, self.labels)

    def getUsers(self, change_time, rack_id, rack_locs):
        users = list()
        userTimeDict = self.userAppHistory[change_time]
        for user_id, rssis in userTimeDict.items():
            locs = self.clf.classifier.predict(np.array(rssis))
            userloc = max(map(lambda x: (np.sum(locs == x), x), locs))[1]
            print(user_id, locs, userloc)
            if rack_id is not None and rack_locs is not None:
                if userloc in rack_locs:
                    users.append(user_id)
            else:
                users.append(user_id)
        return users


class UserEvent():
    def __init__(self, user_id, event):
        self.userId = user_id
        self.event = event


class UserLoc():
    def __init__(self, user_id, rssi_time, user_loc, device="camera"):
        self.userId = user_id
        self.rssiTime = rssi_time
        self.loc = user_loc
        self.device = device


class FindUser():
    def __init__(self, rack_id, change_time):
        self.rackId = rack_id
        self.changeTime = change_time


class FindUserLoc():
    def __init__(self, user_id, rssi_time, rssis):
        self.userId = user_id
        self.rssiTime = rssi_time
        self.rssis = rssis


class TrainRssis():
    def __init__(self, train_id, rssis):
        self.trainId = train_id
        self.rssis = rssis
