from thespian.actors import ActorSystem
from bvps.logger import logcfg

print("-"*100)
actor_system = ActorSystem(systemBase="multiprocTCPBase", logDefs=logcfg)
print("init actor system:{}".format(actor_system))
print("-"*100)
