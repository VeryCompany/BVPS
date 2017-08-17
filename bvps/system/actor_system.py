from thespian.actors import ActorSystem
from bvps.logger import logcfg

print("-" * 100)
capabilities = {'': True, 'Admin Port': 1900}
actor_system = ActorSystem(
    systemBase="multiprocTCPBase", logDefs=logcfg, capabilities=capabilities)
print("init actor system:{}".format(actor_system))
print("-" * 100)
