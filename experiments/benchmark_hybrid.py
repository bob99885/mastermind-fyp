"""Hybrid solver benchmark entry point."""

from backend.solvers.hybrid_solver import HybridSolver


SOLVER_NAME = "Hybrid"
SOLVER_CLASS = HybridSolver


if __name__ == "__main__":
	print(f"{SOLVER_NAME} solver benchmark uses the shared benchmark runner.")
