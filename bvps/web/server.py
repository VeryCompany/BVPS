# -*- coding: utf-8 -*-
import sys
import os
import logging as log
import multiprocessing
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import SocketServer
import cv2


def draw_center_line(frame):
    vv = frame.shape
    h = vv[0]
    w = vv[1]
    cv2.line(frame, (0, h / 2), (w, h / 2), (255, 0, 0), 1)
    cv2.line(frame, (w / 2, 0), (w / 2, h), (255, 0, 0), 1)
    cv2.circle(frame, (w / 2, h / 2), 63, (0, 0, 255), 1)


class VideoHandler(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def _set_images_header(self):
        self.send_response(200)
        self.send_header('Content-type',
                         'multipart/x-mixed-replace; boundary=frame')
        self.end_headers()

    def do_GET(self):
        if self.path == "/feed":
            self.send_response(200)
            self.send_header('Content-type',
                             'multipart/x-mixed-replace; boundary=frame')
            self.end_headers()
            while True:
                try:
                    """Video streaming generator function."""
                    frame, t0, sec = WebServer.queue.get()
                    draw_center_line(frame)
                    ret, jpg = cv2.imencode(".jpeg", frame)
                    self.wfile.write(b'--frame\r\n')
                    self.wfile.write(b'Content-Type: image/jpeg\r\n\r\n')
                    self.end_headers()
                    self.wfile.write(bytearray(jpg))
                    self.wfile.write(b'\r\n')
                except:
                    pass
        if self.path == "/feed":
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write("<html><body><h1>ok!</h1></body></html>")

        return

    def do_HEAD(self):
        self._set_headers()

    def do_POST(self):
        # Doesn't do anything with posted data
        self._set_headers()
        self.wfile.write("<html><body><h1>POST!</h1></body></html>")


class WebServer(multiprocessing.Process):
    def __init__(self, queue, port):
        multiprocessing.Process.__init__(self)
        self.port = port
        WebServer.queue = queue

    def run(self):
        server_address = ('', self.port)
        httpd = HTTPServer(server_address, VideoHandler)
        print 'Starting httpd...'
        httpd.serve_forever()


if __name__ == '__main__':
    web = WebServer(multiprocessing.Queue(), 10000)

    web.start()
