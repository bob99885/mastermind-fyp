from backend.game.evaluator import evaluate_guess
from backend.solvers.entropy_solver import EntropySolver
from backend.solvers.adaptive_solver import AdaptiveSolver
from backend.solvers.genetic_solver import GeneticSolver
from backend.solvers.hybrid_solver import HybridSolver
from backend.solvers.knuth_solver import KnuthSolver
from backend.solvers.minimax_solver import MinimaxSolver
from backend.solvers.random_solver import RandomSolver


SOLVER_TYPES = {
	"entropy": EntropySolver,
	"genetic": GeneticSolver,
	"hybrid": HybridSolver,
	"knuth": KnuthSolver,
	"minimax": MinimaxSolver,
	"random": RandomSolver,
	"adaptive": AdaptiveSolver,
}

SOLVER_LABELS = {
	"hybrid": "HERF Hybrid (50/30/20)",
}


def run_solver(solver_name, secret, max_guesses=1296):
	normalized_name = solver_name.lower()
	solver_type = SOLVER_TYPES.get(normalized_name)

	if solver_type is None:
		raise ValueError(f"Unknown solver: {solver_name}")

	solver = (
		solver_type()
		if normalized_name != "random"
		else solver_type(list(__import__("backend.game.code_space", fromlist=["generate_code_space"]).generate_code_space()))
	)
	history = []
	solver_history = []

	for guess_number in range(1, max_guesses + 1):
		if normalized_name == "genetic":
			guess = solver.make_guess(solver_history)
		else:
			guess = solver.next_guess()

		feedback = evaluate_guess(secret, guess)
		entry = {
			"guess": list(guess),
			"black": feedback[0],
			"white": feedback[1],
		}
		if normalized_name == "adaptive":
			entry["strategy"] = solver.strategy_name
			entry["reason"] = solver.reason
			entry["candidates_before"] = solver.candidate_count_before
			history.append(entry)
		else:
			history.append(entry)
		solver_history.append((guess, feedback))

		if feedback[0] == 4:
			return {
				"solver": SOLVER_LABELS.get(normalized_name, normalized_name),
				"solved": True,
				"guesses": guess_number,
				"history": history
			}

		if hasattr(solver, "update"):
			solver.update(feedback)

	return {
		"solver": normalized_name,
		"solved": False,
		"guesses": max_guesses,
		"history": history
	}
