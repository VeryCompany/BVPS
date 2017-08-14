# numpy: image and matice computation
import numpy as np
# mxnet: deep learning
import mxnet as mx
# argparse: command line parsing
import argparse
# cv2: opencv image processing
import cv2
import time
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


def test_net(prefix=['model/pnet', 'model/rnet', 'model/onet'], epoch=[16, 16, 16], batch_size=[2048, 256, 16], ctx=mx.cpu(0),
             thresh=[0.6, 0.6, 0.7], min_face_size=24,
             stride=2, camera_path='0'):

    # load pnet model
    args, auxs = load_param(prefix[0], epoch[0], convert=True, ctx=ctx)
    PNet = FcnDetector(P_Net("test"), ctx, args, auxs)

    # load rnet model
    args, auxs = load_param(prefix[1], epoch[0], convert=True, ctx=ctx)
    RNet = Detector(R_Net("test"), 24, batch_size[1], ctx, args, auxs)

    # load onet model
    args, auxs = load_param(prefix[2], epoch[2], convert=True, ctx=ctx)
    ONet = Detector(O_Net("test"), 48, batch_size[2], ctx, args, auxs)

    mtcnn_detector = MtcnnDetector(detectors=[PNet, RNet, ONet], ctx=ctx, min_face_size=min_face_size,
                                   stride=stride, threshold=thresh, slide_window=False)

    try:
        capture = cv2.VideoCapture(int(camera_path))
    except ValueError as e:
        capture = cv2.VideoCapture(camera_path)

    first_loop = True
    while (capture.isOpened()):
        ret, img = capture.read()
        if img is None:
            continue

        # Initialize video writing
        if (first_loop):
            first_loop = False
            fourcc = cv2.VideoWriter_fourcc(*'H264')
            h, w = img.shape[:2]
            writer = cv2.VideoWriter('test.mkv', fourcc, 10, (w, h), True)

        t1 = time.time()

        boxes, boxes_c = mtcnn_detector.detect_pnet(img)
        boxes, boxes_c = mtcnn_detector.detect_rnet(img, boxes_c)
        boxes, boxes_c = mtcnn_detector.detect_onet(img, boxes_c)

        print('shape: ', img.shape, '--', 'time: ', time.time() - t1)

        draw = img.copy()
        if boxes_c is not None:
            font = cv2.FONT_HERSHEY_SIMPLEX
            for b in boxes_c:
                cv2.rectangle(draw, (int(b[0]), int(b[1])), (int(b[2]), int(b[3])), (0, 255, 255), 1)
                cv2.putText(draw, '%.3f' % b[4], (int(b[0]), int(b[1])), font, 0.4, (255, 255, 255), 1)

        cv2.imshow("detection result", draw)
        writer.write(draw)

        k = cv2.waitKey(1)
        if k == 27 or k == 113:  # Esc or q key to stop
            writer.release()
            cv2.destroyAllWindows()
            break


def parse_args():
    parser = argparse.ArgumentParser(description='Test mtcnn',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--prefix', dest='prefix', help='prefix of model name', nargs="+",
                        default=['model/pnet', 'model/rnet', 'model/onet'], type=str)
    parser.add_argument('--epoch', dest='epoch', help='epoch number of model to load', nargs="+",
                        default=[16, 16, 16], type=int)
    parser.add_argument('--batch_size', dest='batch_size', help='list of batch size used in prediction', nargs="+",
                        default=[2048, 256, 16], type=int)
    parser.add_argument('--thresh', dest='thresh', help='list of thresh for pnet, rnet, onet', nargs="+",
                        default=[0.5, 0.5, 0.7], type=float)
    parser.add_argument('--min_face', dest='min_face', help='minimum face size for detection',
                        default=40, type=int)
    parser.add_argument('--stride', dest='stride', help='stride of sliding window',
                        default=2, type=int)
    parser.add_argument('--sw', dest='slide_window', help='use sliding window in pnet', action='store_true')
    parser.add_argument('--gpu', dest='gpu_id', help='GPU device to train with',
                        default=0, type=int)
    parser.add_argument('--camera-path', dest='camera_path', help='camera path pass to cv2.videoCapture',
                        default=0, type=str)
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = parse_args()
    print('Called with argument:')
    print(args)
    ctx = mx.gpu(args.gpu_id)
    if args.gpu_id == -1:
        ctx = mx.cpu(0)
    test_net(args.prefix, args.epoch, args.batch_size,
             ctx, args.thresh, args.min_face,
             args.stride, camera_path=args.camera_path)
