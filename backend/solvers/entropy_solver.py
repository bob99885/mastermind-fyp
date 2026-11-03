from collections import defaultdict
from math import log2

from backend.game.code_space import generate_code_space
from backend.game.evaluator import evaluate_guess


class EntropySolver:

    def __init__(self):

        self.candidates = generate_code_space()
        self.guess_space = generate_code_space()

        self.last_guess = None

    def next_guess(self):
        if len(self.candidates) == 1:
            self.last_guess = self.candidates[0]
            return self.last_guess

        best_guess = None
        best_entropy = -1

        for guess in self.guess_space:

            feedback_counts = defaultdict(int)

            for secret in self.candidates:

                feedback = evaluate_guess(
                    secret,
                    guess
                )

                feedback_counts[feedback] += 1

            entropy = 0

            total = len(self.candidates)

            for count in feedback_counts.values():

                probability = count / total

                entropy -= probability * log2(
                    probability
                )

            if entropy > best_entropy:

                best_entropy = entropy

                best_guess = guess

        self.last_guess = best_guess

        return best_guess

    def update(self, feedback):

        self.candidates = [

            code

            for code in self.candidates

            if evaluate_guess(
                code,
                self.last_guess
            ) == feedback
        ]