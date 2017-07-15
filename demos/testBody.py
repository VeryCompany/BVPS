import numpy as np
import cv2
video = cv2.VideoCapture("rtsp://192.168.0.177:554")
cascade = cv2.CascadeClassifier("haarcascade_upperbody.xml")
nested = cv2.CascadeClassifier("haarcascade_frontalface_alt.xml")
from common import clock, draw_str


def detect(img, cascade):
    rects = cascade.detectMultiScale(img, scaleFactor=3, minNeighbors=1, minSize=(80, 80),
                                     flags=cv2.CASCADE_SCALE_IMAGE)
    if len(rects) == 0:
        return []
    rects[:,2:] += rects[:,:2]
    return rects
def draw_rects(img, rects, color):
    for x1, y1, x2, y2 in rects:
        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
while True:
    ret, img = video.read()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)

    t = clock()
    rects = detect(gray, cascade)
    vis = img.copy()
    draw_rects(vis, rects, (0, 255, 0))

    dt = clock() - t

    draw_str(vis, (20, 20), 'time: %.1f ms' % (dt*1000))
    #cv2.imshow('facedetect', gray)
    cv2.imshow('facedetect2', vis)
    if cv2.waitKey(5) == 27:
        break
cv2.destroyAllWindows()
