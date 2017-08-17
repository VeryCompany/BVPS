from socketserver import BaseRequestHandler, ThreadingUDPServer
from rpsc.controls import ControlCenter


class BeaconLocServer(BaseRequestHandler):
    def handle(self):
        data = self.request[0].decode('utf-8').strip()
        user_info = eval(str(data).replace("=", ":"),
                         {"time": "rssi_time", "phoneonlynum": "userId", "map": "rssis", "type": "data_type",
                          "id": "train_id"})

        if "data_type" in user_info:
            data_type = user_info["data_type"]
            if int(data_type) == 1:
                user_id = None
                rssi_time = None
                rssis = None
                if "userId" in user_info:
                    user_id = user_info["userId"]
                if "rssi_time" in user_info:
                    rssi_time = user_info["rssi_time"]
                if "rssis" in user_info:
                    rssis = user_info["rssis"]
                if user_id is not None and rssi_time is not None and rssis is not None:
                    if len(rssis) > 5:
                        ControlCenter.send_human_rssi(str(user_id), rssis, rssi_time)
                    else:
                        print("data less ... ")
            elif int(data_type) == 2:
                train_id = None
                rssis = None
                if "train_id" in user_info:
                    train_id = user_info["train_id"]
                if "rssis" in user_info:
                    rssis = user_info["rssis"]
                if train_id is not None and rssis is not None:
                    if len(rssis) > 6:
                        ControlCenter.train_rssis(train_id, rssis)
                    else:
                        print("train data less . ")
                        pass


def start_udp():
    host, port = "", 8990
    server = ThreadingUDPServer((host, port), BeaconLocServer)
    server.serve_forever()
