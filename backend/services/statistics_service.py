import csv
from pathlib import Path


RESULTS_FILE = Path(__file__).resolve().parents[2] / "results" / "csv" / "benchmark_results.csv"


def get_benchmark_results():
	if not RESULTS_FILE.exists() or RESULTS_FILE.stat().st_size == 0:
		return []

	with RESULTS_FILE.open(newline="") as file:
		return list(csv.DictReader(file))


def get_solver_results():
	results = {}

	for row in get_benchmark_results():
		solver = row.get("solver") or row.get("Solver")
		if not solver:
			continue

		average = row.get("average") or row.get("avg") or row.get("average_guesses")
		average = average or row.get("Average")
		worst = row.get("worst") or row.get("worst_case") or row.get("max_guesses") or row.get("Worst")
		results[solver] = {
			"avg": float(average) if average else None,
			"worst": int(float(worst)) if worst else None,
			"best": int(float(row["Best"])) if row.get("Best") else None,
			"runtime": float(row["RuntimeSeconds"]) if row.get("RuntimeSeconds") else None
		}

	return results
