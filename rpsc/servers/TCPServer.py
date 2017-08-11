from socketserver import ThreadingTCPServer, StreamRequestHandler
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
                print("TCP server receive from (%r):%s" % (self.client_address, data))
                dataMsg += data
                while True:
                    if len(dataMsg) >= 7:
                        if dataMsg[0] == 0x55:
                            print(dataMsg[0])
                            cmd = dataMsg[1]
                            opt = dataMsg[2]
                            if cmd == 0xAA:
                                if opt == 0xBB:
                                    ControlCenter.send_loc_product_msg(dataMsg[3:5], "02")
                                elif opt == 0xCC:
                                    ControlCenter.send_loc_product_msg(dataMsg[3:5], "01")
                                else:
                                    pass
                                dataMsg = dataMsg[7:]
                            elif cmd == 0xAB:
                                if opt == 0xBB:
                                    ControlCenter.send_weight_product_msg(dataMsg[3:5], "02")
                                elif opt == 0xCC:
                                    ControlCenter.send_weight_product_msg(dataMsg[3:5], "01")
                                else:
                                    pass
                                dataMsg = dataMsg[7:]
                            else:
                                dataMsg = dataMsg[2:]
                        else:
                            dataMsg = dataMsg[1:]
                    else:
                        break
                self.wfile.write(b"\x00")
            except Exception as dataReceiveErr:
                print(self.client_address, "TcpServer Error:", dataReceiveErr)
                self.request.close()
                break


def start_tcp(asys):
    ControlCenter.set_asys(asys)
    host = ''
    port = 8999
    address = (host, port)
    ControlCenter.init_rack()
    server = ThreadingTCPServer(address, RackServer)

    print("start tcp server port %d" % port)
    server.serve_forever()
