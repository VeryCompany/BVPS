# import multiprocessing
import threading
from .servers import TCPServer, HTTPServer, UDPServer, TCPPhoneServer


def server_start(asys):
    t1 = threading.Thread(target=TCPServer.start_tcp, args=(asys,))
    t2 = threading.Thread(target=HTTPServer.start_http, args=(asys,))
    t3 = threading.Thread(target=UDPServer.start_udp)
    t4 = threading.Thread(target=TCPPhoneServer.start_phone_tcp, args=(asys,))

    t1.start()
    t2.start()
    t3.start()
    t4.start()


if __name__ == "__main__":
    # p1 = multiprocessing.Process(target=TCPServer.startTCP)
    # p2 = multiprocessing.Process(target=HTTPServer.startHTTP)
    #
    # p1.start()
    # p2.start()
    # serverStart()
    pass
