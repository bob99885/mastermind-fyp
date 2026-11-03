from backend.game.code_space import generate_code_space
from backend.game.evaluator import evaluate_guess
from backend.solvers.entropy_solver import EntropySolver
from backend.solvers.minimax_solver import MinimaxSolver
from backend.solvers.knuth_solver import KnuthSolver


class AdaptiveSolver:
    def __init__(self):
        self.candidates = generate_code_space()
        self.last_guess = None
        self.strategy = None
        self.strategy_name = None
        self.reason = "Starting with information gain across the full candidate space"
        self.candidate_count_before = len(self.candidates)

    def choose_strategy(self):
        candidate_count = len(self.candidates)
        if candidate_count > 100:
            return "entropy", "Large candidate space: maximise expected information gain"
        if candidate_count > 20:
            return "minimax", "Candidate space narrowed: minimise the worst remaining partition"
        return "knuth", "Small candidate space: use exact candidate pruning"

    def next_guess(self):
        strategy_name, self.reason = self.choose_strategy()
        self.strategy_name = strategy_name
        self.strategy = {
            "entropy": EntropySolver,
            "minimax": MinimaxSolver,
            "knuth": KnuthSolver,
        }[strategy_name]()
        self.strategy.candidates = self.candidates[:]
        self.candidate_count_before = len(self.candidates)
        self.last_guess = self.strategy.next_guess()
        return self.last_guess

    def update(self, feedback):
        self.candidates = [
            code for code in self.candidates
            if evaluate_guess(code, self.last_guess) == feedback
        ]
        self.strategy.candidates = self.candidates[:]
