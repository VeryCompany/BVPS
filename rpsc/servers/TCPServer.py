from SocketServer import ThreadingTCPServer, StreamRequestHandler
from rpsc.controls import ControlCenter

dataMsg = bytes()

class RackServer(StreamRequestHandler):
    def handle(self):
        global dataMsg
        while True:
            try:
                data = self.request.recv(1024)
                if not data:
                    return

                #print "receive from (%r):%s" % (self.client_address, data)
                dataMsg += data
                while True:
                    if len(dataMsg) >= 7:
                        if ord(dataMsg[0]) == 0x55:
                            cmd = ord(dataMsg[1:2])
                            opt = ord(dataMsg[2:3])
                            if cmd == 0xAA:
                                if opt == 0xBB:
                                    ControlCenter.sendLocProductMsg(dataMsg[3:5], "02")
                                elif opt == 0xCC:
                                    ControlCenter.sendLocProductMsg(dataMsg[3:5], "01")
                                else:
                                    pass
                                dataMsg = dataMsg[7:]
                            elif cmd == 0xAB:
                                if opt == 0xBB:
                                    ControlCenter.sendWeightProductMsg(dataMsg[3:5], "02")
                                elif opt == 0xCC:
                                    ControlCenter.sendWeightProductMsg(dataMsg[3:5], "01")
                                else:
                                    pass
                                dataMsg = dataMsg[7:]
                            else:
                                dataMsg = dataMsg[2:]
                        else:
                            dataMsg = dataMsg[1:]
                    else:
                        break
                self.wfile.write("00".decode("hex"))
            except Exception as dataReceiveErr:
                print self.client_address, "TcpServer Error:", dataReceiveErr
                self.request.close()
                break

def startTCP(asys):
    ControlCenter.setAsys(asys)
    HOST = ''
    PORT = 8999
    ADDR = (HOST, PORT)
    ControlCenter.initRack()
    server = ThreadingTCPServer(ADDR, RackServer)

    print "start server port %d" % PORT
    server.serve_forever()