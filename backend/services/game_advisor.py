"""Explainable decision support for the next Mastermind guess."""

from collections import Counter, defaultdict
from math import log2

from backend.game.code_space import generate_code_space
from backend.game.constants import NUM_COLORS, PEGS_PER_COLOR
from backend.game.evaluator import evaluate_guess


HERF_WEIGHTS = {
    "entropy": 0.5,
    "expected_elimination": 0.3,
    "minimax_reduction": 0.2,
}

HERF_METHODOLOGY = (
    "Entropy is the primary objective because it maximises expected information "
    "gain. Expected elimination rewards average candidate-space reduction, while "
    "minimax reduction limits poor worst-case partitions. These are reasoned "
    "heuristic priorities, not mathematically proven optimal weights."
)


def _partition(candidates, guess):
    partitions = defaultdict(int)
    for candidate in candidates:
        partitions[evaluate_guess(candidate, guess)] += 1
    return partitions


def _metrics(partitions, candidate_count):
    expected_remaining = sum(
        size * size for size in partitions.values()
    ) / candidate_count
    entropy = -sum(
        (size / candidate_count) * log2(size / candidate_count)
        for size in partitions.values()
    )
    return entropy, expected_remaining, max(partitions.values())


def _filter_state(history, colour_inventory):
    codes = generate_code_space()
    candidates = codes
    for entry in history:
        feedback = (entry["black"], entry["white"])
        candidates = [
            code for code in candidates
            if evaluate_guess(code, tuple(entry["guess"])) == feedback
        ]
    valid_guesses = [
        guess for guess in codes
        if all(count <= colour_inventory.get(colour, 0)
               for colour, count in Counter(guess).items())
    ]
    if not candidates:
        raise ValueError("No possible codes match the recorded feedback.")
    return candidates, valid_guesses


def get_game_advice(history, colour_inventory=None, limit=3):
    """Return candidate-space metrics, ranked moves, and outcome explanations."""
    colour_inventory = colour_inventory or {
        colour: PEGS_PER_COLOR for colour in range(1, NUM_COLORS + 1)
    }
    candidates, valid_guesses = _filter_state(history, colour_inventory)
    candidate_count = len(candidates)
    candidate_set = set(candidates)
    if candidate_count == 1 and candidates[0] in valid_guesses:
        only_guess = candidates[0]
        return {
            "candidate_count": 1,
            "colour_inventory": colour_inventory,
            "hybrid_weights": HERF_WEIGHTS,
            "hybrid_methodology": HERF_METHODOLOGY,
            "total_remaining": sum(colour_inventory.values()),
            "criteria": _criterion_leaders([{
                "guess": only_guess, "entropy": 0,
                "expected_remaining": 1, "worst_case_remaining": 1,
                "elimination_rate": 0, "hybrid_score": 1,
            }]),
            "recommendations": [_recommendation(
                only_guess, 0, 1, 1, 0, 100, 1, {}, candidate_count,
                "This is the only code consistent with the recorded feedback.", 0,
                {"entropy": 0, "expected_elimination": 0, "minimax_reduction": 0},
            )],
        }

    scored = []
    for guess in valid_guesses:
        partitions = _partition(candidates, guess)
        entropy, expected_remaining, worst_case_remaining = _metrics(
            partitions, candidate_count
        )
        scored.append({
            "guess": guess,
            "entropy": entropy,
            "expected_remaining": expected_remaining,
            "worst_case_remaining": worst_case_remaining,
            "elimination_rate": 1 - expected_remaining / candidate_count,
            "partitions": partitions,
            "solve_chance": 100 / candidate_count if guess in candidate_set else 0,
        })

    max_entropy = max(item["entropy"] for item in scored) or 1
    max_elimination = max(item["elimination_rate"] for item in scored) or 1
    max_minimax_reduction = max(
        candidate_count - item["worst_case_remaining"] for item in scored
    ) or 1
    for item in scored:
        item["hybrid_score"] = (
            HERF_WEIGHTS["entropy"] * item["entropy"] / max_entropy
            + HERF_WEIGHTS["expected_elimination"]
            * item["elimination_rate"] / max_elimination
            + HERF_WEIGHTS["minimax_reduction"]
            * (candidate_count - item["worst_case_remaining"])
            / max_minimax_reduction
        )
        item["hybrid_components"] = {
            "entropy": HERF_WEIGHTS["entropy"] * item["entropy"] / max_entropy,
            "expected_elimination": (
                HERF_WEIGHTS["expected_elimination"]
                * item["elimination_rate"] / max_elimination
            ),
            "minimax_reduction": (
                HERF_WEIGHTS["minimax_reduction"]
                * (candidate_count - item["worst_case_remaining"])
                / max_minimax_reduction
            ),
        }

    ranked = sorted(scored, key=lambda item: (
        -item["hybrid_score"], item["worst_case_remaining"], item["guess"]
    ))
    recommendations = []
    for item in ranked[:limit]:
        reduction = round(item["elimination_rate"] * 100, 1)
        reason = (
            f"HERF score {item['hybrid_score']:.3f}: "
            f"{item['entropy']:.2f} bits of expected information, "
            f"rules out {reduction:.1f}% on average, and leaves at most "
            f"{item['worst_case_remaining']} candidates."
        )
        recommendations.append(_recommendation(
            item["guess"], item["entropy"], item["expected_remaining"],
            item["worst_case_remaining"], reduction, item["solve_chance"],
            item["hybrid_score"], item["partitions"], candidate_count, reason,
            item["elimination_rate"], item["hybrid_components"]
        ))

    return {
        "candidate_count": candidate_count,
        "colour_inventory": colour_inventory,
        "hybrid_weights": HERF_WEIGHTS,
        "hybrid_methodology": HERF_METHODOLOGY,
        "total_remaining": sum(colour_inventory.values()),
        "criteria": _criterion_leaders(scored),
        "recommendations": recommendations,
    }


def get_algorithm_analysis(history, colour_inventory=None):
    """Compare Entropy and Minimax and expose every outcome bucket."""
    colour_inventory = colour_inventory or {
        colour: PEGS_PER_COLOR for colour in range(1, NUM_COLORS + 1)
    }
    candidates, valid_guesses = _filter_state(history, colour_inventory)
    candidate_count = len(candidates)
    if candidate_count == 1:
        only_guess = candidates[0]
        algorithm_explanations = {
            "entropy": (
                "Only one code is consistent with the recorded feedback, "
                "so this is the guaranteed solution."
            ),
            "minimax": (
                "Only one code is consistent with the recorded feedback, "
                "so this is the guaranteed solution."
            ),
        }
        algorithms = {}
        for name in ("entropy", "minimax"):
            algorithms[name] = {
                "name": "Entropy" if name == "entropy" else "Minimax",
                "recommended_guess": list(only_guess),
                "explanation": algorithm_explanations[name],
                "metrics": {
                    "entropy_bits": 0,
                    "expected_elimination_percent": 0,
                    "expected_remaining": 1,
                    "worst_case_remaining": 1,
                },
                "distribution": [{
                    "black": 4,
                    "white": 0,
                    "count": 1,
                    "probability": 100.0,
                }],
            }
        return {
            "n": sum(colour_inventory.values()),
            "candidate_count": candidate_count,
            "criteria_checked": [
                "entropy", "expected_elimination",
                "expected_remaining", "minimax_worst_case",
            ],
            "algorithms": algorithms,
        }

    scored = []
    for guess in valid_guesses:
        partitions = _partition(candidates, guess)
        entropy, expected_remaining, worst_case_remaining = _metrics(
            partitions, candidate_count
        )
        scored.append({
            "guess": guess,
            "partitions": partitions,
            "entropy": entropy,
            "expected_remaining": expected_remaining,
            "worst_case_remaining": worst_case_remaining,
            "expected_elimination": 1 - expected_remaining / candidate_count,
        })

    selected = {
        "entropy": max(scored, key=lambda item: (
            item["entropy"], -item["worst_case_remaining"]
        )),
        "minimax": min(scored, key=lambda item: (
            item["worst_case_remaining"], -item["entropy"]
        )),
    }
    algorithms = {}
    for name, item in selected.items():
        algorithms[name] = {
            "name": "Entropy" if name == "entropy" else "Minimax",
            "recommended_guess": list(item["guess"]),
            "explanation": (
                "Maximises Shannon information gain so likely feedback "
                "partitions are as informative as possible."
                if name == "entropy" else
                "Minimises the largest possible feedback partition, "
                "protecting against the worst next state."
            ),
            "metrics": {
                "entropy_bits": round(item["entropy"], 3),
                "expected_elimination_percent": round(
                    item["expected_elimination"] * 100, 1
                ),
                "expected_remaining": round(item["expected_remaining"], 1),
                "worst_case_remaining": item["worst_case_remaining"],
            },
            "distribution": _outcome_distribution(
                item["partitions"], candidate_count
            ),
        }
    return {
        "n": sum(colour_inventory.values()),
        "candidate_count": candidate_count,
        "criteria_checked": [
            "entropy", "expected_elimination",
            "expected_remaining", "minimax_worst_case",
        ],
        "algorithms": algorithms,
    }


def _criterion_leaders(scored):
    return {
        "hybrid": list(min(scored, key=lambda item: (
            -item["hybrid_score"], item["worst_case_remaining"]
        ))["guess"]),
        "entropy": list(max(scored, key=lambda item: (
            item["entropy"], -item["worst_case_remaining"]
        ))["guess"]),
        "expected_remaining": list(min(
            scored, key=lambda item: (
                item["expected_remaining"], item["worst_case_remaining"]
            )
        )["guess"]),
        "minimax": list(min(scored, key=lambda item: (
            item["worst_case_remaining"], -item["entropy"]
        ))["guess"]),
    }


def _recommendation(
    guess, entropy, expected_remaining, worst_case_remaining,
    expected_reduction, solve_chance, hybrid_score, partitions,
    candidate_count, reason, elimination_rate, hybrid_components
):
    return {
        "guess": list(guess),
        "entropy": round(entropy, 3),
        "expected_remaining": round(expected_remaining, 1),
        "worst_case_remaining": worst_case_remaining,
        "expected_reduction": expected_reduction,
        "criterion_scores": {
            "entropy_bits": round(entropy, 3),
            "expected_elimination_percent": expected_reduction,
            "expected_remaining": round(expected_remaining, 1),
            "worst_case_remaining": worst_case_remaining,
            "hybrid_score": round(hybrid_score, 3),
            "hybrid_contributions": {
                name: round(value, 3)
                for name, value in hybrid_components.items()
            },
        },
        "solve_chance": round(solve_chance, 1),
        "hybrid_score": round(hybrid_score, 3),
        "distribution": _outcome_distribution(partitions, candidate_count),
        "reason": reason,
    }


def _outcome_distribution(partitions, candidate_count):
    return [
        {
            "black": feedback[0],
            "white": feedback[1],
            "count": count,
            "probability": round(count / candidate_count * 100, 1),
        }
        for feedback, count in sorted(partitions.items())
    ]
