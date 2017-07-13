from thespian.actors import ActorSystem
import sys
import os
from camera import CMD

asys = ActorSystem((sys.argv + ['multiprocTCPBase'])[1])
camera1 = asys.createActor('camera.Camera')
camera2 = asys.createActor('camera.Camera')
print dir(asys.capabilities)
print "-------------------"
print list(asys.capabilities)
print "-------------------"
print vars(camera1.addressDetails)
print "-------------------"
#asys.tell(camera1, CMD(1, ts=(0,"b")))

#cameras = {
#    "camera1":asys.createActor('camera.Camera'),
#    "camera2":asys.createActor('camera.Camera'),
#    "camera3":asys.createActor('camera.Camera'),
#    "camera4":asys.createActor('camera.Camera'),
#    "camera5":asys.createActor('camera.Camera')
#}

asys.shutdown()
