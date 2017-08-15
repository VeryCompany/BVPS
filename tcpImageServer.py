from socketserver import ThreadingTCPServer, StreamRequestHandler
import cv2
import pickle


class ImageHandler(StreamRequestHandler):
    def __init__(self, request, client_address, server):
        self.dataMsg = bytes()
        StreamRequestHandler.__init__(self, request, client_address, server)

    def setup(self):
        StreamRequestHandler.setup(self)

    def finish(self):
        StreamRequestHandler.finish(self)

    def handle(self):
        while True:
            try:
                data = self.request.recv(30720 * 10000)
                if not data:
                    return
                print("TCP phone server receive from (%r):%s" % (self.client_address, data))
                self.dataMsg += data
                print(self.dataMsg)
                result = pickle.loads(self.dataMsg)
                # cv2.imwrite("image.png", result)
                # print(result, result.shape)
                self.wfile.write(self.dataMsg)
            except Exception as dataReceiveErr:
                print(self.client_address, "TcpServer Error:", dataReceiveErr)
                self.request.close()
                break


def start_phone_tcp():
    host = ''
    port = 8992
    address = (host, port)

    server = ThreadingTCPServer(address, ImageHandler)
    print("start phone server port %d" % port)

    server.serve_forever()


if __name__ == "__main__":
    start_phone_tcp()
