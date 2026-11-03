from collections import Counter


def evaluate_guess(secret, guess):

    black = sum(
        s == g
        for s, g in zip(secret, guess)
    )

    secret_counter = Counter(secret)
    guess_counter = Counter(guess)

    common = sum(
        min(secret_counter[c], guess_counter[c])
        for c in secret_counter
    )

    white = common - black

    return black, white