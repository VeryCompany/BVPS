class TrainingCMD(object):
    def __init__(self, cctype, msg, uid=None):
        self.cctype = cctype
        self.msg = msg
        self.uid = uid

a =  TrainingCMD(1, 1, uid=1)

import inspect

inspect.getmro(a.__class__)




"lh".encode('ascii', 'ignore')
