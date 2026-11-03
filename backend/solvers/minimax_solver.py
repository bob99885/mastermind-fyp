from collections import defaultdict

from backend.game.code_space import generate_code_space
from backend.game.evaluator import evaluate_guess


class MinimaxSolver:

    def __init__(self):

        self.candidates = generate_code_space()
        self.guess_space = generate_code_space()

        self.last_guess = None

    def next_guess(self):
        if len(self.candidates) == 1:
            self.last_guess = self.candidates[0]
            return self.last_guess

        best_guess = None
        best_score = float("inf")

        for guess in self.guess_space:

            partitions = defaultdict(int)

            for secret in self.candidates:

                feedback = evaluate_guess(
                    secret,
                    guess
                )

                partitions[feedback] += 1

            worst_case = max(partitions.values())

            if worst_case < best_score:

                best_score = worst_case
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