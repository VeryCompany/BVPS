# -*- coding: utf-8 -*-
import sys
import os
import logging as log
import multiprocessing
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import SocketServer
import cv2
class VideoHandler(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
    def _set_images_header(self):
        self.send_response(200)
        self.send_header('Content-type', 'multipart/x-mixed-replace; boundary=frame')
        self.end_headers()
    def do_GET(self):
        if self.path == "/feed":
            self.send_response(200)
            self.send_header('Content-type', 'multipart/x-mixed-replace; boundary=frame')
            self.end_headers()
            while True:
                """Video streaming generator function."""
                frame = WebServer.queue.get()
                ret,jpg = cv2.imencode(".jpeg",frame)
                self.wfile.write(b'--frame\r\n')
                self.wfile.write(b'Content-Type: image/jpeg\r\n\r\n')
                self.end_headers()
                self.wfile.write (bytearray(jpg))
                self.wfile.write (b'\r\n')
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

    def __init__(self,queue,port):
        multiprocessing.Process.__init__(self)
        self.port = port
        WebServer.queue = queue

    def run(self):
        server_address = ('', self.port)
        httpd = HTTPServer(server_address, VideoHandler)
        print 'Starting httpd...'
        httpd.serve_forever()

if __name__ == '__main__':
    web = WebServer(multiprocessing.Queue(),10000)

    web.start()
