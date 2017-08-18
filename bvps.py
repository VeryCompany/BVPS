from thespian.actors import ActorSystem
from bvps.logger import logcfg
import time

print("-" * 100)
capabilities = {'': True, 'torch': None, 'Admin Port': 1900}
actor_system = ActorSystem(
    systemBase="multiprocTCPBase", logDefs=logcfg, capabilities=capabilities)
print("init actor system:{}".format(actor_system))
print("-" * 100)

actor_system._systemBase.deRegisterRemoteSystem('192.168.0.172')
