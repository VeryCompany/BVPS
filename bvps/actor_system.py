from thespian.actors import ActorSystem
from bvps.logger import logcfg

print("-"*100)
actor_system = ActorSystem(systemBase="multiprocQueueBase", logDefs=logcfg)
print("init actor system:{}".format(actor_system))
print("-"*100)
