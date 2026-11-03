"""Exhaustively compare HERF weightings across every Mastermind secret."""

import csv
import sys
from collections import defaultdict
from math import log2
from pathlib import Path
from statistics import mean, median, stdev

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.game.code_space import generate_code_space
from backend.game.evaluator import evaluate_guess


WEIGHTINGS = {
    "entropy_only": (1.0, 0.0, 0.0),
    "70_20_10": (0.7, 0.2, 0.1),
    "60_25_15": (0.6, 0.25, 0.15),
    "50_30_20": (0.5, 0.3, 0.2),
    "40_30_30": (0.4, 0.3, 0.3),
    "40_20_40": (0.4, 0.2, 0.4),
    "33_33_34": (0.33, 0.33, 0.34),
}


def choose_guess(candidates, guess_space, weights):
    candidate_count = len(candidates)
    scored = []
    for guess in guess_space:
        partitions = defaultdict(int)
        for secret in candidates:
            partitions[evaluate_guess(secret, guess)] += 1
        entropy = -sum(
            (size / candidate_count) * log2(size / candidate_count)
            for size in partitions.values()
        )
        expected_remaining = sum(
            size * size for size in partitions.values()
        ) / candidate_count
        worst_case = max(partitions.values())
        scored.append((
            guess,
            entropy,
            1 - expected_remaining / candidate_count,
            candidate_count - worst_case,
            worst_case,
        ))

    max_entropy = max(item[1] for item in scored) or 1
    max_elimination = max(item[2] for item in scored) or 1
    max_reduction = max(item[3] for item in scored) or 1
    return max(
        scored,
        key=lambda item: (
            weights[0] * item[1] / max_entropy
            + weights[1] * item[2] / max_elimination
            + weights[2] * item[3] / max_reduction,
            -item[4],
            item[0],
        ),
    )[0]


def solve(secret, code_space, weights):
    candidates = code_space
    guesses = 0
    while True:
        guess = choose_guess(candidates, code_space, weights)
        guesses += 1
        feedback = evaluate_guess(secret, guess)
        if feedback[0] == 4:
            return guesses
        candidates = [
            code for code in candidates
            if evaluate_guess(code, guess) == feedback
        ]


def run():
    code_space = generate_code_space()
    rows = []
    for name, weights in WEIGHTINGS.items():
        results = [solve(secret, code_space, weights) for secret in code_space]
        rows.append({
            "Weighting": name,
            "EntropyWeight": weights[0],
            "EliminationWeight": weights[1],
            "MinimaxWeight": weights[2],
            "AverageGuesses": f"{mean(results):.4f}",
            "MedianGuesses": f"{median(results):.1f}",
            "StdDevGuesses": f"{stdev(results):.4f}",
            "BestCase": min(results),
            "WorstCase": max(results),
        })

    output = Path("results/csv/herf_weighting_results.csv")
    with output.open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    for row in rows:
        print(",".join(str(value) for value in row.values()))


if __name__ == "__main__":
    run()
