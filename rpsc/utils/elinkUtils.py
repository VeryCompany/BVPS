import random

ids = []


def get_next_random_id():
    rid = random.randint(0, 10000)
    if rid in ids:
        return get_next_random_id()
    else:
        ids.append(rid)
        return rid
