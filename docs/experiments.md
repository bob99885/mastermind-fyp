# Experiments

The experiments evaluate the six implemented solvers:

- Random
- Knuth
- Entropy
- Minimax
- HERF Hybrid (50/30/20)
- Genetic

## Method

Guess-count benchmarks record the number of guesses required to identify a
secret code. Runtime benchmarks measure solver execution with
`time.perf_counter()` through the shared helper in
`backend/benchmark/profiler.py`.

The evaluation metrics are:

- Average number of guesses
- Best-case guesses
- Worst-case guesses
- Runtime in seconds per game
- Improvement over the Random baseline

## Running Experiments

Run the reproducible runtime benchmark from the project root:

```bash
venv/bin/python experiments/benchmark_runtime.py
```

Run the Random guess-count benchmark with:

```bash
venv/bin/python -m backend.benchmark.benchmark_runner
```

The solver-specific files in `experiments/` are lightweight entry-point
wrappers. Shared benchmark logic remains in `backend/benchmark/` to avoid
duplicating experiment code.

## Outputs

- CSV results are stored in `results/csv/`.
- Generated charts are stored in `results/graphs/`.
- The final comparison table is documented in `docs/results_summary.md`.
- Test evidence is documented in `tests/test_results.md`.
