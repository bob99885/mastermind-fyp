"""Route catalogue for the Flask API implemented in ``app.py``."""


API_ROUTES = {
	"home": {
		"path": "/",
		"method": "GET",
		"description": "API root",
	},
	"health": {
		"path": "/health",
		"method": "GET",
		"description": "Health check",
	},
	"new_game": {
		"path": "/new-game",
		"method": "POST",
		"description": "Create a computer or player-secret game",
	},
	"guess": {
		"path": "/guess",
		"method": "POST",
		"description": "Submit player guess",
	},
	"history": {
		"path": "/history",
		"method": "GET",
		"description": "Current game guess history",
	},
	"game_distribution": {
		"path": "/game/distribution",
		"method": "GET",
		"description": "Predicted feedback distributions for recommended guesses",
	},
	"game_algorithm_analysis": {
		"path": "/game/algorithm-analysis",
		"method": "GET",
		"description": "Entropy and Minimax comparison with full feedback distributions",
	},
	"solver_run": {
		"path": "/solver/run",
		"method": "POST",
		"description": "Run selected solver, including adaptive strategy",
	},
	"statistics": {
		"path": "/statistics",
		"method": "GET",
		"description": "Benchmark statistics",
	},
	"solver_results": {
		"path": "/solver-results",
		"method": "GET",
		"description": "Structured solver metrics",
	},
	"player_analytics": {
		"path": "/player-analytics",
		"method": "GET",
		"description": "Human game performance analytics",
	},
	"graph_file": {
		"path": "/graphs/<filename>",
		"method": "GET",
		"description": "Generated benchmark graph asset",
	},
}


if __name__ == "__main__":
	for route_name, route in API_ROUTES.items():
		print(f"{route['method']} {route['path']} ({route_name})")
