# Adaptive Statistical Strategies for Mastermind

An interactive Mastermind platform for comparing search strategies, measuring solver performance, and analysing human play.

## Features

- Human play with computer-generated or player-defined secret codes
- Entropy, Minimax, Knuth, Hybrid, Genetic, Random, and Adaptive Statistical solvers
- Adaptive strategy switching: Entropy for large candidate spaces, Minimax for medium spaces, and Knuth-style pruning for small spaces
- Explainable adaptive solver output with strategy reasons and candidate-space reduction
- SQLite-backed player game history and human performance analytics
- Benchmark tables, charts, zoomable graph views, and solver comparison commentary
- Explainable decision support with candidate filtering, entropy, minimax, expected elimination, and HERF hybrid recommendations
- Feedback-outcome distributions for each recommended guess

## Explainable decision support

During play, the advisor filters the complete 6^4 code space using the recorded
guess/feedback history. It scores legal next guesses using four criteria:

- **Entropy**: expected information gain
- **Expected candidates**: expected number of candidates left after feedback
- **Minimax**: smallest worst-case candidate partition
- **HERF hybrid**: 50% entropy, 30% expected elimination, and 20% minimax reduction.
  The three suggestions are all ranked by this same hybrid score. Each metric is
  normalized against the best legal guess before weighting, and the API exposes
  each recommendation's weighted contributions. The weights are transparent
  heuristic priorities: entropy leads because it measures expected information
  gain, expected elimination rewards average candidate-space reduction, and
  minimax reduction limits poor worst-case partitions. They are not claimed to
  be mathematically optimal.

The play screen shows the leader for each criterion, three hybrid recommendations,
the natural-language reason for each recommendation, and the predicted feedback
distribution (for example, `1B 2W`) for every recommendation.

The **FYP analyst** compares two algorithms in the live game:

- **Entropy** selects the guess with the highest expected Shannon information gain.
- **Minimax** selects the guess with the smallest worst-case remaining candidate set.

The analyst reports `n = 60` for the available peg pool, checks entropy, expected
elimination, expected remaining candidates, and minimax worst-case size, and shows
every possible feedback bucket for both selected guesses. The same data is
available at `GET /game/algorithm-analysis`.

## Run locally

```bash
python3 -m pip install -r requirements.txt
python3 app.py
```

Open `frontend/pages/home.html` or `frontend/pages/solver_demo.html` in a browser. The Flask API runs on `http://127.0.0.1:5001`.

Run the tests with:

```bash
python3 -m pytest -q
```

## Public deployment

The app is deployment-ready for a Python host or Docker service. The production
container uses Gunicorn and binds to the provider's `PORT`; it is not intended
to be exposed using Flask's development server.

For a public URL, push this project to GitHub and create a web service on a
host such as Render, Railway, Fly.io, or a VPS. Use:

```text
Build command: pip install -r requirements.txt
Start command: gunicorn --bind 0.0.0.0:$PORT --workers 2 --access-logfile - app:app
Health check path: /health
```

After deployment, the provider gives you an HTTPS URL that works on other
devices. A public URL is not automatically indexed by Google; submit the URL
or sitemap in Google Search Console and allow time for crawling.

## Research surface

The project compares algorithmic performance using average guesses, worst-case guesses, runtime, candidate-space reduction, and human-vs-solver metrics. Player sessions are stored in `mastermind.db`, while benchmark results remain in `results/csv/`.

The research question is: **Does HERF improve the trade-off between average and
worst-case solving performance compared with entropy-only, expected-elimination,
and minimax strategies?** The hypotheses are that HERF will reduce average
guesses while preserving a competitive worst-case bound, and that increasing
minimax weight will improve worst-case protection at a possible average-cost.

Entropy, minimax, and HERF now evaluate the complete legal 1,296-code guess
space at each decision; there is no hidden 50-guess approximation. The
five-secret measurements in `results/csv/benchmark_results.csv` are an
operational comparison, not exhaustive evidence. Run
`python3 experiments/benchmark_herf_weights.py` for an all-1,296-secret
weighting comparison. It reports mean, median, standard deviation, best case,
and worst case for each weighting. The checked-in comparison table is a
historical five-secret snapshot and must be regenerated before making final
performance claims.
