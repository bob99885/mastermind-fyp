"""Summary metrics for guess-count benchmark results."""


def _require_results(results):
	if not results:
		raise ValueError("Benchmark results cannot be empty")


def average_guesses(results):
	_require_results(results)
	return sum(results) / len(results)


def best_case(results):
	_require_results(results)
	return min(results)


def worst_case(results):
	_require_results(results)
	return max(results)
