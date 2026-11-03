from collections import Counter

from backend.game.constants import NUM_COLORS, NUM_PEGS, PEGS_PER_COLOR
from backend.game.generator import generate_secret
from backend.game.evaluator import evaluate_guess


class Mastermind:

    def __init__(self, secret=None, mode="computer"):
        if mode not in {"computer", "player"}:
            raise ValueError("Mode must be computer or player")
        if mode == "player" and secret is None:
            raise ValueError("Player mode requires a secret code")
        if secret is None:
            secret = generate_secret()
        if (
            not isinstance(secret, (list, tuple))
            or len(secret) != NUM_PEGS
            or any(not isinstance(value, int) or not 1 <= value <= NUM_COLORS for value in secret)
        ):
            raise ValueError("Secret must contain four numbers from 1 to 6")

        self.secret = tuple(secret)
        self.mode = mode
        self.history = []
        self.game_over = False
        self.remaining_colour_counts = {
            colour: PEGS_PER_COLOR
            for colour in range(1, NUM_COLORS + 1)
        }

    def guess(self, code):

        if self.game_over:
            raise ValueError("This game is over. Start a new game first.")

        guess_counts = Counter(code)
        for colour, count in guess_counts.items():
            if count > self.remaining_colour_counts.get(colour, 0):
                raise ValueError(f"Not enough pegs of colour {colour} remain.")

        feedback = evaluate_guess(
            self.secret,
            code
        )

        for colour, count in guess_counts.items():
            self.remaining_colour_counts[colour] -= count

        self.history.append({
            "guess": list(code),
            "black": feedback[0],
            "white": feedback[1]
        })

        if feedback[0] == len(self.secret):
            self.game_over = True
        elif sum(self.remaining_colour_counts.values()) < NUM_PEGS:
            self.game_over = True

        return feedback