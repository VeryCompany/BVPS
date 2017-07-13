def main(portnum):
    asys = ActorSystem('multiprocUDPBase')
    try:
        server = asys.createActor(ServerActor)
        handler = asys.createActor(Handler)
        asys.tell(server, StartServer(portnum, handler))
        print('Hit Ctrl-C to exit')
        try:
            signal.pause()
        except KeyboardInterrupt:
            pass
        print('Shutting down')
        asys.tell(server, ActorExitRequest())
        asys.tell(handler, ActorExitRequest())
    finally:
        asys.shutdown()



if __name__ == '__main__':
    main(int((sys.argv + [8080])[1]))
