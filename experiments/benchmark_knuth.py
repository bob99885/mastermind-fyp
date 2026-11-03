"""Knuth solver benchmark entry point."""

from backend.solvers.knuth_solver import KnuthSolver


SOLVER_NAME = "Knuth"
SOLVER_CLASS = KnuthSolver


if __name__ == "__main__":
	print(f"{SOLVER_NAME} solver benchmark uses the shared benchmark runner.")
