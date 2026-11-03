from itertools import product
from backend.game.constants import *

def generate_code_space():

    return list(
        product(
            range(1, NUM_COLORS + 1),
            repeat=NUM_PEGS
        )
    )