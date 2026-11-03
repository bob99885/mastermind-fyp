from backend.game.code_space import generate_code_space
from backend.game.evaluator import evaluate_guess


class KnuthSolver:

    def __init__(self):

        self.candidates = generate_code_space()

        self.last_guess = None

    def next_guess(self):

        self.last_guess = self.candidates[0]

        return self.last_guess

    def update(self, feedback):

        black, white = feedback

        new_candidates = []

        for code in self.candidates:

            result = evaluate_guess(
                code,
                self.last_guess
            )

            if result == (black, white):
                new_candidates.append(code)

        self.candidates = new_candidates