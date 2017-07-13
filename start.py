from thespian.actors import ActorSystem
import sys
import os
from camera import CMD
asys = ActorSystem((sys.argv + ['multiprocTCPBase'])[1])
camera1 = asys.createActor('camera.Camera',globalName ='camera1')
camera2 = asys.createActor('camera.Camera',globalName ='camera1')
asys.tell(camera1, CMD(1, ts=(0,"b")))

#asys.shutdown()
