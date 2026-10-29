import random

def spin_roulette():
    """
    Geeft winst of verlies terug.
    """

    roll = random.randint(1, 100)

    if roll <= 48:
        return 10
    else:
        return -10