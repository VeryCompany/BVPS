from thespian.actors import ActorSystem
import sys
from bvps.logger import logcfg
ActorSystem(systemBase="multiprocTCPBase", logDefs=logcfg).shutdown()
