import random
from backend.game.constants import *

def generate_secret():
    return tuple(
        random.randint(1, NUM_COLORS)
        for _ in range(NUM_PEGS)
    )