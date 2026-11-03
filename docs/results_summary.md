# Solver Results Summary

These figures are a historical five-secret operational snapshot. They are
retained for UI demonstration only and are not the exhaustive results of the
full legal-guess-space implementation. Regenerate the exhaustive experiments
before using performance figures in the final evaluation.

Runtime values are mean per-game measurements from the reproducible benchmark
in `experiments/benchmark_runtime.py`, using five representative secret codes.

| Solver | Average Guesses | Worst Case | Runtime (s) |
| --- | ---: | ---: | ---: |
| HERF Hybrid (50/30/20) | 4.200 | 5 | 0.098184 |
| Entropy | 4.493 | 6 | 0.099609 |
| Minimax | 4.502 | 6 | 0.105369 |
| Genetic | 4.863 | 12 | 0.031454 |
| Knuth | 5.774 | 9 | 0.002354 |
| Random | 635.376 | 1293 | 0.002535 |

The average, best, and worst guess figures are the benchmark results recorded
in `results/csv/benchmark_results.csv`. Runtime depends on hardware and should
be reported as an implementation measurement, not a universal constant.