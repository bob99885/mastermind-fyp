# Algorithms

This project implements seven Mastermind solving strategies. Each solver receives
feedback as black and white peg counts and uses it to select or filter future
guesses.

## Implemented Solvers

- **Random:** selects an unused candidate code at random.
- **Knuth:** filters the candidate space using previous feedback.
- **Entropy:** selects a guess that maximizes the expected information gain.
- **Minimax:** selects a guess that minimizes the largest remaining candidate
	partition.
- **HERF Hybrid (50/30/20):** combines normalized entropy (50%), expected
  candidate elimination (30%), and minimax reduction (20%). Entropy prioritises
  expected information gain, elimination rewards average search-space reduction,
  and minimax reduction protects against poor worst-case partitions.

Entropy, Minimax, and HERF score every code in the legal 1,296-code guess
space. This makes the solver decisions reproducible and avoids presenting a
truncated candidate sample as an optimum.
- **Genetic:** evolves candidate codes according to their agreement with the
	observed guess history.
- **Adaptive Statistical:** switches between entropy, minimax, and Knuth-style
	pruning as the candidate space becomes smaller.

The shared game engine evaluates exact-position matches as black pegs and
correct-color, wrong-position matches as white pegs. Codes use four positions
and six colors represented by the values 1 through 6.

## Finite Color Pool

Each game starts with ten physical pegs of each color, for an initial pool of
60. During a guess, a selected peg is held out of the live pool; submitting
the guess consumes those four pegs for the rest of the game. Removing a peg
from an unsubmitted guess returns it to the pool. In Game 2, setting the
player-defined secret is separate from the codebreaker's pool.

The displayed color distribution assumes each remaining physical peg is
equally likely to be selected next. For color `i`, with `n_i` pegs left in a
pool of `N` pegs, the conditional probability is:

$$P(C_i \mid \text{remaining pool}) = \frac{n_i}{N}, \qquad
N = \sum_{j=1}^{6} n_j.$$

For example, after selecting one blue peg from a full pool, the next-peg
probability for blue is $9/59 \approx 15.3\%$; each other color is
$10/59 \approx 16.9\%$. These are pool-selection probabilities, not
probabilities that a color occurs in the hidden code. The move advisor's
expected candidate reduction is reported separately.

## Comparison Metrics

The solvers are compared using:

- Average number of guesses
- Best-case guesses
- Worst-case guesses
- Average runtime per game

The current benchmark summary is available in
`results/csv/benchmark_results.csv` and `docs/results_summary.md`.
