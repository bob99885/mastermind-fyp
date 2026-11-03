"""Entropy solver benchmark entry point."""

from backend.solvers.entropy_solver import EntropySolver


SOLVER_NAME = "Entropy"
SOLVER_CLASS = EntropySolver


if __name__ == "__main__":
	print(f"{SOLVER_NAME} solver benchmark uses the shared benchmark runner.")
