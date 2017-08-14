# numpy: image and matice computation
import numpy as np
# mxnet: deep learning
import mxnet as mx
# symbol: define the network structure
from core.symbol import P_Net, R_Net, O_Net
# detector: bind weight with structure and create a detector class
from core.detector import Detector
# fcn_detector: bind weight with structure and create a detector class
from core.fcn_detector import FcnDetector
# load_model: load model from .param file
from tools.load_model import load_param
# MtcnnDetector: concatenate the three networks
from core.MtcnnDetector import MtcnnDetector
from bvps.common import CameraType, mtnnDir
import traceback
import logging as log

print("_"*100)
print("init common")
print("_"*100)


def test_net(self,
             prefix=[
                 os.path.join(mtnnDir, 'pnet'),
                 os.path.join(mtnnDir, 'rnet'),
                 os.path.join(mtnnDir, 'onet')
             ],
             epoch=[16, 16, 16],
             batch_size=[2048, 256, 16],
             ctx=mx.gpu(0),
             thresh=[0.5, 0.5, 0.7],
             min_face_size=40,
             stride=2):
    try:
        # load pnet model
        args, auxs = load_param(prefix[0], epoch[0], convert=True, ctx=ctx)
        PNet = FcnDetector(P_Net("test"), ctx, args, auxs)

        # load rnet model
        args, auxs = load_param(prefix[1], epoch[0], convert=True, ctx=ctx)
        RNet = Detector(R_Net("test"), 24, batch_size[1], ctx, args, auxs)

        # load onet model
        args, auxs = load_param(prefix[2], epoch[2], convert=True, ctx=ctx)
        ONet = Detector(O_Net("test"), 48, batch_size[2], ctx, args, auxs)

        mtcnn_detector = MtcnnDetector(
            detectors=[PNet, RNet, ONet],
            ctx=ctx,
            min_face_size=min_face_size,
            stride=stride,
            threshold=thresh,
            slide_window=False)
        return mtcnn_detector
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        log.error(
            traceback.format_exception(exc_type, exc_value, exc_traceback))
