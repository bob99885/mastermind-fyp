"""Minimax solver benchmark entry point."""

from backend.solvers.minimax_solver import MinimaxSolver


SOLVER_NAME = "Minimax"
SOLVER_CLASS = MinimaxSolver


if __name__ == "__main__":
	print(f"{SOLVER_NAME} solver benchmark uses the shared benchmark runner.")
