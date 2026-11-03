from collections import defaultdict
from math import log2

from backend.game.evaluator import evaluate_guess
from backend.solvers.entropy_solver import EntropySolver


HERF_WEIGHTS = (0.5, 0.3, 0.2)


class HybridSolver(EntropySolver):

    def __init__(self):
        super().__init__()

    def next_guess(self):
        if len(self.candidates) == 1:
            self.last_guess = self.candidates[0]
            return self.last_guess

        candidate_count = len(self.candidates)
        scored = []

        for guess in self.guess_space:
            partitions = defaultdict(int)
            for secret in self.candidates:
                partitions[evaluate_guess(secret, guess)] += 1

            entropy = -sum(
                (size / candidate_count) * log2(size / candidate_count)
                for size in partitions.values()
            )
            expected_remaining = sum(
                size * size for size in partitions.values()
            ) / candidate_count
            worst_case_remaining = max(partitions.values())
            scored.append({
                "guess": guess,
                "entropy": entropy,
                "elimination": 1 - expected_remaining / candidate_count,
                "minimax_reduction": candidate_count - worst_case_remaining,
                "worst_case_remaining": worst_case_remaining,
            })

        max_entropy = max(item["entropy"] for item in scored) or 1
        max_elimination = max(item["elimination"] for item in scored) or 1
        max_minimax_reduction = max(
            item["minimax_reduction"] for item in scored
        ) or 1

        best_guess = max(
            scored,
            key=lambda item: (
                HERF_WEIGHTS[0] * item["entropy"] / max_entropy
                + HERF_WEIGHTS[1] * item["elimination"] / max_elimination
                + HERF_WEIGHTS[2] * item["minimax_reduction"] / max_minimax_reduction,
                -item["worst_case_remaining"],
                item["guess"],
            ),
        )["guess"]
        self.last_guess = best_guess
        return best_guess
