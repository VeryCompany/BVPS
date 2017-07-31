# import multiprocessing
import threading
from servers import TCPServer, HTTPServer

def serverStart(asys):
    t1 = threading.Thread(target=TCPServer.startTCP,args=(asys,))
    t2 = threading.Thread(target=HTTPServer.startHTTP,args=(asys,))

    t1.start()
    t2.start()

if __name__ == "__main__":
    # p1 = multiprocessing.Process(target=TCPServer.startTCP)
    # p2 = multiprocessing.Process(target=HTTPServer.startHTTP)
    #
    # p1.start()
    # p2.start()
    # serverStart()
    pass

