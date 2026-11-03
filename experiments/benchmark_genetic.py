"""Genetic solver benchmark entry point."""

from backend.solvers.genetic_solver import GeneticSolver


SOLVER_NAME = "Genetic"
SOLVER_CLASS = GeneticSolver


if __name__ == "__main__":
	print(f"{SOLVER_NAME} solver benchmark uses the shared benchmark runner.")
