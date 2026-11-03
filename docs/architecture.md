```mermaid
flowchart TD
	A[Frontend HTML and JavaScript] --> B[Flask API]
	B --> C[Mastermind Game Engine]
	B --> D[Solver Service]
	B --> E[Statistics Service]
	D --> R[Random Solver]
	D --> K[Knuth Solver]
	D --> H[Entropy Solver]
	D --> M[Minimax Solver]
	D --> Y[HERF Hybrid Solver]
	D --> G[Genetic Solver]
	E --> F[Benchmark CSV and PNG Graphs]
```

## Request Flow

The frontend sends guesses and solver requests to Flask. The API delegates game
evaluation to the Mastermind engine and solver requests to the solver service.
Benchmark data is read by the statistics service and rendered by the statistics
page.
