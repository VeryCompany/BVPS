import pickle
# from rpsc.utils.fpLocalize import RoomClassifier

beacon = [23042, 22403, 22816, 22723, 22887]

trainData = [
    [10] * 5, [10] * 5, [10] * 5, [10] * 5, [10] * 5, [10] * 5, [10] * 5, [10] * 5, [10] * 5, [10] * 5
]

# 1: left rack left
# 2: door left
# 3: door right
# 4: right rack right
# 5 left rack and door center
# 6 right door and rack center
label = list()
label.extend([0] * 10)
# label.extend([1]*135)
# label.extend([2]*260)

# clf = RoomClassifier()
# clf.fit(trainData, label)
#
# rssis = [[-69, -72, -74, -70, -65], [-76, -73, -67, -74, -67], [-64, -80, -70, -83, -73], [-72, -63, -63, -66, -71]]
# locs = clf.classifier.predict(rssis)
# print(locs, max(map(lambda x: (np.sum(locs==x), x), locs))[1])

with open("./traindatas", 'wb') as outfile:
    pickle.dump({
        'fingerprints': trainData,
        'label': label
    }, outfile)
