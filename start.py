from thespian.actors import ActorSystem
import sys
import os
from camera import CMD
asys = ActorSystem((sys.argv + ['multiprocTCPBase'])[1])
