"""Random solver benchmark entry point.

The shared benchmark implementations live in ``benchmark_runtime.py`` and
``backend/benchmark/benchmark_runner.py``.
"""

from backend.solvers.random_solver import RandomSolver


SOLVER_NAME = "Random"
SOLVER_CLASS = RandomSolver


if __name__ == "__main__":
	print(f"{SOLVER_NAME} solver benchmark uses the shared benchmark runner.")
