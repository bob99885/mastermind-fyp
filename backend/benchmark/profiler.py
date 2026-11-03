"""Small runtime measurement helpers for solver experiments."""

from time import perf_counter


def measure_runtime(function, *args, **kwargs):
	started = perf_counter()
	result = function(*args, **kwargs)
	elapsed = perf_counter() - started
	return result, elapsed
