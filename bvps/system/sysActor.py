from thespian.actors import *
import logging
class SystemActor(ActorTypeDispatcher):
    def __init__(self, *args, **kw):
        logging.info("system actor started")
    def receiveMsg_str(self, message, sender):
        logging.info("received msg {}".format(message))
