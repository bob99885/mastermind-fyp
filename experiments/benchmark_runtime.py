import csv
import sys
from pathlib import Path
from statistics import mean

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.game.code_space import generate_code_space
from backend.benchmark.profiler import measure_runtime as profile_runtime
from backend.game.evaluator import evaluate_guess
from backend.services.solver_service import run_solver
from backend.solvers.random_solver import RandomSolver


SOLVERS = ("Random", "Knuth", "Entropy", "Minimax", "Hybrid", "Genetic")
SECRETS = [
    (1, 2, 3, 4),
    (6, 5, 4, 3),
    (2, 2, 5, 6),
    (1, 1, 1, 1),
    (6, 6, 6, 6),
]


def measure_runtime(solver_name, secret):
    def run_solver_once():
        if solver_name == "Random":
            solver = RandomSolver(generate_code_space())
            for _ in range(1296):
                guess = solver.next_guess()
                if evaluate_guess(secret, guess)[0] == 4:
                    break
        else:
            run_solver(solver_name.lower(), secret)

    _, elapsed = profile_runtime(run_solver_once)
    return elapsed


def run():
    rows = []
    for solver_name in SOLVERS:
        runtimes = [measure_runtime(solver_name, secret) for secret in SECRETS]
        rows.append({
            "Solver": solver_name,
            "RuntimeSeconds": f"{mean(runtimes):.6f}"
        })

    with open("results/csv/runtime_results.csv", "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["Solver", "RuntimeSeconds"])
        writer.writeheader()
        writer.writerows(rows)

    for row in rows:
        print(f"{row['Solver']},{row['RuntimeSeconds']}")


if __name__ == "__main__":
    run()