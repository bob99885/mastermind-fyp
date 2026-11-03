"""Tests for solver construction and the shared solver service."""

import pytest

from backend.services.solver_service import run_solver
from backend.solvers.entropy_solver import EntropySolver
from backend.solvers.genetic_solver import GeneticSolver
from backend.solvers.hybrid_solver import HybridSolver
from backend.solvers.knuth_solver import KnuthSolver
from backend.solvers.minimax_solver import MinimaxSolver
from backend.solvers.random_solver import RandomSolver


@pytest.mark.parametrize(
	"solver_type",
	[
		EntropySolver,
		GeneticSolver,
		HybridSolver,
		KnuthSolver,
		MinimaxSolver,
	],
)
def test_solver_creation(solver_type):
	solver = solver_type()

	assert solver is not None


def test_random_solver_creation():
	solver = RandomSolver([(1, 2, 3, 4)])

	assert solver.next_guess() == (1, 2, 3, 4)


@pytest.mark.parametrize("solver_name", ["knuth", "entropy", "minimax", "hybrid", "genetic"])
def test_solver_service_solves_fixed_code(solver_name):
	result = run_solver(solver_name, (1, 2, 3, 4))

	assert result["solved"] is True
	assert result["guesses"] == len(result["history"])


def test_adaptive_solver_explains_strategy():
	result = run_solver("adaptive", (1, 2, 3, 4))

	assert result["solved"] is True
	assert result["history"][0]["strategy"] == "entropy"
	assert result["history"][0]["candidates_before"] == 1296
	assert result["history"][0]["reason"]


def test_unknown_solver_is_rejected():
	with pytest.raises(ValueError, match="Unknown solver"):
		run_solver("unknown", (1, 2, 3, 4))
