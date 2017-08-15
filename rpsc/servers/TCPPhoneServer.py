from socketserver import ThreadingTCPServer, StreamRequestHandler


class PhoneHandler(StreamRequestHandler):
    def __init__(self, request, client_address, server):
        self.dataMsg = bytes()
        self.deviceId = None
        StreamRequestHandler.__init__(self, request, client_address, server)

    def setup(self):
        StreamRequestHandler.setup(self)

    def finish(self):
        if self.deviceId is not None:
            self.server.remove_client((self.deviceId, self))
        StreamRequestHandler.finish(self)

    def handle(self):
        while True:
            try:
                data = hex_to_byte(self.request.recv(1024).decode())
                if not data:
                    return
                # print("TCP phone server receive from (%r):%s" % (self.client_address, data))
                self.dataMsg += data
                if len(self.dataMsg) >= 10:
                    if self.dataMsg[0] == 0x7E:
                        cmd = self.dataMsg[1]
                        if cmd == 0x01:
                            print("heart beat")
                            if self.deviceId is None:
                                self.deviceId = bytes_to_hex(self.dataMsg[2:10])
                                print(type(self.deviceId))
                                self.server.add_client((self.deviceId, self))
                            self.dataMsg = self.dataMsg[11:]
                        elif cmd == 0x02:
                            print("message")
                        else:
                            print("other")
                    else:
                        self.dataMsg = self.dataMsg[1:]
                self.wfile.write(b"00")
            except Exception as dataReceiveErr:
                print(self.client_address, "Tcp Phone Server Error:", dataReceiveErr)
                self.request.close()
                break


def bytes_to_hex(data_bytes):
    return ''.join(["%02X" % x for x in data_bytes]).strip()


def hex_to_byte(data_hex):
    return bytes.fromhex(data_hex)


class PhoneServer(ThreadingTCPServer):
    def __init__(self, server_address, request_handler_class):
        ThreadingTCPServer.__init__(self, server_address, request_handler_class, True)
        self.clients = set()

    def add_client(self, client):
        """Register a client with the internal store of clients."""
        already_add = False
        for server_id, socket_server in self.clients:
            if server_id == client[0]:
                already_add = True
                break
        if not already_add:
            self.clients.add(client)
        print(self.clients)

    def remove_client(self, client):
        """Take a client off the register to disable broadcasts to it."""
        already_remove = True
        for server_id, socket_server in self.clients:
            if server_id == client[0]:
                already_remove = False
                break
        if not already_remove:
            try:
                self.clients.remove(client)
            except Exception as removeClientErr:
                print("remove client err:", removeClientErr)


def start_phone_tcp(asys):
    from rpsc.controls import ControlCenter
    ControlCenter.set_asys(asys)
    host = ''
    port = 8991
    address = (host, port)

    server = PhoneServer(address, PhoneHandler)
    print("start phone tcp server port %d" % port)

    phone_center = PhoneCenter(server)
    ControlCenter.set_phone_center(phone_center)
    server.serve_forever()


class PhoneCenter:
    server = None

    def __init__(self, phone_server):
        self.server = phone_server

    def send_msg2phone(self, phone_id, msg_type, message=None):
        if msg_type == "1":
            product_id = message["productId"]
            product_sign_id = message["productSignId"]
            send_msg = "7E01" + "|" + str(product_id) + "|" + str(product_sign_id) + "|" + "7E"
            self.send_msg(phone_id, send_msg)
        elif msg_type == "2":
            send_msg = "7E027E"
            self.send_msg(phone_id, send_msg)

    def send_msg(self, phone_id, msg):
        for device_id, socket_ser in self.server.clients:
            print(device_id)
            if device_id == "0" + phone_id and socket_ser is not None:
                print("send msg. ->", msg)
                socket_ser.wfile.write(msg.encode("ascii"))
