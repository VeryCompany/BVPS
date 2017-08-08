from thespian.actors import *
import logging
import SocketServer

class MyTCPHandler(SocketServer.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        #print "{} wrote:".format(self.client_address[0])
        #print self.data
        # just send back the same data, but upper-cased
        self.request.sendall(self.data.upper())

class SystemActor(ActorTypeDispatcher):
    def __init__(self, *args, **kw):
        logging.info("system actor started")

    def receiveMsg_str(self, message, sender):
        logging.info("received msg {}".format(message))
