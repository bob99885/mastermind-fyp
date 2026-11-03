"""Tests for black- and white-peg evaluation."""

from backend.game.evaluator import evaluate_guess


def test_exact_match():
	black, white = evaluate_guess((1, 2, 3, 4), (1, 2, 3, 4))

	assert black == 4
	assert white == 0


def test_all_colors_present_but_misplaced():
	black, white = evaluate_guess((1, 2, 3, 4), (4, 3, 2, 1))

	assert black == 0
	assert white == 4


def test_duplicate_colors_are_counted_once_per_match():
	black, white = evaluate_guess((1, 1, 2, 2), (1, 2, 3, 3))

	assert black == 1
	assert white == 1
