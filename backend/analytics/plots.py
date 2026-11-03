from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from backend.analytics.solver_results import SOLVER_RESULTS
from backend.benchmark.performance import improvement_percentage


OUTPUT_DIR = Path(__file__).resolve().parents[2] / "results" / "graphs"


# ----------------------------------
# Graph 1
# Overall comparison (log scale)
# ----------------------------------

def overall_average_chart(output_path=OUTPUT_DIR / "average_log.png"):

    names = list(SOLVER_RESULTS.keys())

    averages = [
        SOLVER_RESULTS[s]["avg"]
        for s in names
    ]

    plt.figure(figsize=(12, 7))

    bars = plt.bar(names, averages)

    plt.yscale("log")

    plt.title(
        "Average Number of Guesses by Solver (Log Scale)",
        fontsize=16
    )

    plt.xlabel("Solver")
    plt.ylabel("Average Guesses")

    for bar, value in zip(bars, averages):

        plt.text(
            bar.get_x() + bar.get_width()/2,
            value * 1.05,
            f"{value:.3f}",
            ha="center",
            fontsize=10,
            fontweight="bold"
        )

    plt.grid(
        axis="y",
        linestyle="--",
        alpha=0.4
    )

    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


# ----------------------------------
# Graph 2
# Intelligent solver comparison
# ----------------------------------

def intelligent_solver_chart(output_path=OUTPUT_DIR / "intelligent_solver.png"):

    names = [
        "HERF Hybrid (50/30/20)",
        "Entropy",
        "Minimax",
        "Genetic",
        "Knuth"
    ]

    averages = [
        SOLVER_RESULTS[s]["avg"]
        for s in names
    ]

    plt.figure(figsize=(10, 6))

    bars = plt.bar(names, averages)

    for bar in bars:

        height = bar.get_height()

        plt.text(
            bar.get_x() + bar.get_width()/2,
            height + 0.02,
            f"{height:.3f}",
            ha="center"
        )

    plt.title("Intelligent Solver Comparison")
    plt.xlabel("Solver")
    plt.ylabel("Average Guesses")

    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


# ----------------------------------
# Graph 3
# Worst case comparison
# (without Random)
# ----------------------------------

def worst_case_chart(output_path=OUTPUT_DIR / "worst_case.png"):

    names = [
        "HERF Hybrid (50/30/20)",
        "Entropy",
        "Minimax",
        "Knuth",
        "Genetic"
    ]

    values = [
        SOLVER_RESULTS[s]["worst"]
        for s in names
    ]

    plt.figure(figsize=(10, 6))

    bars = plt.bar(names, values)

    for bar in bars:

        height = bar.get_height()

        plt.text(
            bar.get_x() + bar.get_width()/2,
            height + 0.1,
            f"{height}",
            ha="center"
        )

    plt.title("Worst Case Comparison")
    plt.xlabel("Solver")
    plt.ylabel("Worst-Case Guesses")

    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


# ----------------------------------
# Graph 4
# Ranking line graph
# ----------------------------------

def improvement_chart(output_path=OUTPUT_DIR / "improvement.png"):

    random_avg = SOLVER_RESULTS["Random"]["avg"]

    names = [
        "Knuth",
        "Entropy",
        "Minimax",
        "HERF Hybrid (50/30/20)",
        "Genetic"
    ]

    improvements = []

    for solver in names:

        avg = SOLVER_RESULTS[solver]["avg"]

        improvements.append(improvement_percentage(random_avg, avg))

    plt.figure(figsize=(10, 6))

    bars = plt.bar(
        names,
        improvements,
        color="seagreen"
    )

    for bar, value in zip(bars, improvements):

        plt.text(
            bar.get_x() + bar.get_width()/2,
            value + 0.005,
            f"{value:.2f}%",
            ha="center",
            fontweight="bold"
        )

    plt.title("Performance Improvement over Random Solver")

    plt.xlabel("Solver")
    plt.ylabel("Improvement (%)")

    plt.ylim(99.0, 99.35)

    plt.grid(
        axis="y",
        linestyle="--",
        alpha=0.4
    )

    plt.tight_layout()

    plt.savefig(output_path)
    plt.close()

# ----------------------------------
# Graph 5
# Measuring Runtime
# ----------------------------------
def runtime_chart(output_path=OUTPUT_DIR / "runtime.png"):

    names = list(SOLVER_RESULTS.keys())
    runtimes = [SOLVER_RESULTS[name]["runtime"] for name in names]

    plt.figure(figsize=(10,6))

    bars = plt.bar(
        names,
        runtimes,
        color="orange"
    )

    for bar, value in zip(bars, runtimes):

        plt.text(
            bar.get_x() + bar.get_width()/2,
            value,
            f"{value:.3f}",
            ha="center"
        )

    plt.title(
        "Average Runtime per Game"
    )

    plt.xlabel("Solver")

    plt.ylabel("Seconds")

    plt.tight_layout()

    plt.savefig(output_path)
    plt.close()


def generate_all_charts():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    overall_average_chart()
    intelligent_solver_chart()
    worst_case_chart()
    improvement_chart()
    runtime_chart()
