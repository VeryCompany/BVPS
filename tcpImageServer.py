from socketserver import ThreadingTCPServer, StreamRequestHandler
import pickle
from bvps.torch.torch_neural_net_lutorpy import TorchNeuralNet
import os

fileDir = os.path.dirname(os.path.realpath(__file__))
modelDir = os.path.join(fileDir, 'bvps', 'models')
openfaceModelDir = os.path.join(modelDir, 'openface')

print("modelDir:{}".format(openfaceModelDir))
net = TorchNeuralNet(
    os.path.join(openfaceModelDir, 'nn4.small2.v1.t7'), imgDim=96, cuda=True)


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
                data = self.request.recv(1024 * 1024 * 1024)
                if not data:
                    return
                print(data)
                face = pickle.loads(data)
                rep = net.forward(face)
                if not rep:
                    res = pickle.dumps(rep)
                    self.wfile.wrte(res)
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
