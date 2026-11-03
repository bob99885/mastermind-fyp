import random

class GeneticSolver:

    def __init__(self):
        self.colors = [1,2,3,4,5,6]
        self.code_length = 4

    def random_code(self):
        return tuple(
            random.choice(self.colors)
            for _ in range(self.code_length)
        )

    def fitness(self, candidate, history):
        """
        Higher fitness means candidate agrees
        with previous feedback.
        """

        score = 0

        for guess, feedback in history:

            if self.simulate_feedback(candidate, guess) == feedback:
                score += 1

        return score

    def simulate_feedback(self, secret, guess):

        black = sum(
            s == g
            for s, g in zip(secret, guess)
        )

        common = sum(
            min(secret.count(c), guess.count(c))
            for c in self.colors
        )

        white = common - black

        return (black, white)

    def evolve(self, history,
               population_size=100,
               generations=30,
               mutation_rate=0.1):

        population = [
            self.random_code()
            for _ in range(population_size)
        ]

        for _ in range(generations):

            population.sort(
                key=lambda x:
                self.fitness(x, history),
                reverse=True
            )

            survivors = population[:20]

            new_population = survivors[:]

            while len(new_population) < population_size:

                p1, p2 = random.sample(
                    survivors,
                    2
                )

                cut = random.randint(1,3)

                child = (
                    p1[:cut] +
                    p2[cut:]
                )

                child = list(child)

                for i in range(len(child)):

                    if random.random() < mutation_rate:

                        child[i] = random.choice(
                            self.colors
                        )

                new_population.append(
                    tuple(child)
                )

            population = new_population

        return max(
            population,
            key=lambda x:
            self.fitness(x, history)
        )

    def make_guess(self, history):

        if not history:
            return (1,1,2,2)

        return self.evolve(history)
