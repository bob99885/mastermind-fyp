import random

from backend.solvers.base_solver import BaseSolver


class RandomSolver(BaseSolver):

    def __init__(self, code_space):

        self.candidates = code_space[:]

    def next_guess(self):

        guess = random.choice(
            self.candidates # find out what is "canndidates"
        )

        self.candidates.remove(guess)

        return guess