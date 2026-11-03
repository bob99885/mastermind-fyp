# System Test Matrix

| Test | Expected | Actual | Status |
| --- | --- | --- | --- |
| New Game | New game starts and history clears | `POST /new-game` returned `200`; history was empty across 10 consecutive runs | Pass |
| Submit Guess | Feedback is displayed | `POST /guess` returned black and white peg values plus history | Pass |
| Win Condition | Victory message and attempts are shown | Exact guess returned `won: true` and `attempts: 1` | Pass |
| Guess History | Previous guesses remain visible | Response history contained every submitted guess; frontend renders a table | Pass |
| Hybrid Solver | Solver solves the game | Hybrid solved the fixed test code in repeated runs | Pass |
| All Solver Demo Options | Every solver returns a result | Random, Knuth, Entropy, Minimax, Hybrid, and Genetic returned `200` responses | Pass |
| Invalid Input | User receives validation feedback | Blank, short, zero, and out-of-range guesses returned `400` | Pass |
| Statistics Page | Graphs and metrics are shown | Five PNG files were generated and `/statistics` returned six solver rows | Pass |
| Runtime Benchmark | Runtime is recorded for each solver | `benchmark_results.csv` contains runtime values for all six solvers | Pass |
| Supervisor Demo Flow | Main pages can be visited without API errors | Home, Play, Solver Demo, Statistics, and Compare pages loaded successfully | Pass |
| Repeated New Games | Reset remains stable under repetition | Ten consecutive `POST /new-game` requests returned `200` | Pass |

## Notes

The Random solver can require hundreds of guesses because it searches randomly;
the demo allows the full 1,296-code space. Intelligent solvers complete the
fixed verification code in substantially fewer guesses.