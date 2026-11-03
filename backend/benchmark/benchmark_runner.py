from backend.game.mastermind import Mastermind
from backend.game.code_space import generate_code_space
from backend.benchmark.metrics import average_guesses, best_case, worst_case
from backend.solvers.random_solver import RandomSolver


def run_benchmark():

    results = []

    for _ in range(100):

        game = Mastermind()

        code_space = generate_code_space()

        solver = RandomSolver(code_space)

        guesses = 0

        while True:

            guess = solver.next_guess()

            guesses += 1

            black, white = game.guess(guess)

            if black == 4:
                break

        results.append(guesses)

    print("Average guesses:", average_guesses(results))
    print("Best case:", best_case(results))
    print("Worst case:", worst_case(results))


if __name__ == "__main__":
    run_benchmark()