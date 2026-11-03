class BaseSolver:

    def next_guess(self):
        raise NotImplementedError("Subclasses must implement next_guess")