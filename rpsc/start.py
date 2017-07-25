# import multiprocessing
import threading
from servers import TCPServer, HTTPServer


if __name__ == "__main__":
    # p1 = multiprocessing.Process(target=TCPServer.startTCP)
    # p2 = multiprocessing.Process(target=HTTPServer.startHTTP)
    #
    # p1.start()
    # p2.start()
    t1 = threading.Thread(target=TCPServer.startTCP)
    t2 = threading.Thread(target=HTTPServer.startHTTP)

    t1.start()
    t2.start()

    t1.join()
    t2.join()

