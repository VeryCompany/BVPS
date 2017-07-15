import openface
import cv2


align = openface.AlignDlib("../models/dlib/shape_predictor_68_face_landmarks.dat")
net = openface.TorchNeuralNet("../models/openface/nn4.small2.v1.t7", imgDim=96,cuda=False)

class Face:

    def __init__(self, rep, identity):
        self.rep = rep
        self.identity = identity

    def __repr__(self):
        return "{{id: {}, rep[0:5]: {}}}".format(
            str(self.identity),
            self.rep[0:5]
        )

# Capture device. Usually 0 will be webcam and 1 will be usb cam.
video_capture = cv2.VideoCapture(0)
#video_capture.set(3, 320)
#video_capture.set(4, 240)

confidenceList = []
while True:
    ret, frame = video_capture.read()
    bbs = align.getAllFaceBoundingBoxes(frame)
    for bb in bbs:
        # print(len(bbs))
        landmarks = align.findLandmarks(frame, bb)
        alignedFace = align.align(96, frame, bb,
                                  landmarks=landmarks,
                                  landmarkIndices=openface.AlignDlib.OUTER_EYES_AND_NOSE)
        if alignedFace is None:
            continue
        bl = (bb.left(), bb.bottom())
        tr = (bb.right(), bb.top())
        cv2.rectangle(frame, bl, tr, color=(153, 255, 204),
                      thickness=3)
        for p in openface.AlignDlib.OUTER_EYES_AND_NOSE:
            cv2.circle(frame, center=landmarks[p], radius=3,
                       color=(102, 204, 255), thickness=-1)
    cv2.imshow('', frame)
    # quit the program on the press of key 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
# When everything is done, release the capture
video_capture.release()
cv2.destroyAllWindows()
