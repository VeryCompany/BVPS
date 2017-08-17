from thespian.actors import ActorSystem
from bvps.logger import logcfg

print("-" * 100)
capabilities = {
    'Admin Port': 1901,
    'Convention Address.IPv4': ('192.168.0.163', 1900),
    'torch': True
}
actor_system = ActorSystem(systemBase="multiprocTCPBase", logDefs=logcfg)
print("init actor system:{}".format(actor_system))
print("-" * 100)
