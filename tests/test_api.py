"""API endpoint tests for the Flask application."""

import pytest

import app as app_module


@pytest.fixture
def client():
	app_module.app.config.update(TESTING=True)
	app_module.game = app_module.Mastermind()
	app_module.game_id = None
	return app_module.app.test_client()


def test_health(client):
	response = client.get("/health")

	assert response.status_code == 200
	assert response.get_json() == {"status": "ok"}


def test_frontend_pages_are_served(client):
	assert client.get("/").status_code == 200
	assert client.get("/pages/play.html").status_code == 200
	assert client.get("/pages/solver_demo.html").status_code == 200
	assert client.get("/css/style.css").status_code == 200
	assert client.get("/js/game.js").status_code == 200


def test_new_game_clears_history(client):
	response = client.post("/guess", json={"guess": [1, 2, 3, 4]})
	assert response.status_code == 200

	response = client.post("/new-game")

	assert response.status_code == 200
	assert response.get_json()["history"] == []


def test_guess_returns_feedback_and_history(client):
	response = client.post("/guess", json={"guess": [1, 2, 3, 4]})
	payload = response.get_json()

	assert response.status_code == 200
	assert {"black", "white", "history", "won", "attempts"} <= payload.keys()
	assert len(payload["history"]) == 1


def test_game_advice_uses_feedback_without_returning_secret(client):
	app_module.game = app_module.Mastermind(secret=(1, 2, 3, 4), mode="player")
	client.post("/guess", json={"guess": [1, 1, 1, 1]})

	response = client.get("/game/advice")
	payload = response.get_json()

	assert response.status_code == 200
	assert payload["candidate_count"] < 1296
	assert len(payload["recommendations"]) == 3
	assert "secret" not in payload
	assert all(0 <= item["expected_reduction"] <= 100 for item in payload["recommendations"])
	assert all(item["reason"] for item in payload["recommendations"])
	assert len(payload["outcome_distributions"]) == 3
	assert payload["outcome_distributions"][0]["outcomes"]


def test_game_advice_exposes_hybrid_criteria_and_outcome_distribution(client):
	app_module.game = app_module.Mastermind(secret=(1, 2, 3, 4), mode="player")

	payload = client.get("/game/advice").get_json()

	assert set(payload["criteria"]) == {"entropy", "expected_remaining", "minimax", "hybrid"}
	recommendation = payload["recommendations"][0]
	assert {"entropy", "expected_remaining", "worst_case_remaining", "hybrid_score"} <= recommendation.keys()
	assert recommendation["criterion_scores"]["expected_elimination_percent"] == recommendation["expected_reduction"]
	assert set(payload["hybrid_weights"]) == {
		"entropy", "expected_elimination", "minimax_reduction"
	}
	assert sum(payload["hybrid_weights"].values()) == pytest.approx(1)
	assert sum(recommendation["criterion_scores"]["hybrid_contributions"].values()) == pytest.approx(
		recommendation["hybrid_score"], abs=0.002
	)
	assert sum(item["count"] for item in recommendation["distribution"]) == payload["candidate_count"]
	assert sum(item["probability"] for item in recommendation["distribution"]) == pytest.approx(100, abs=0.2)


def test_game_distribution_exposes_top_level_feedback_outcomes(client):
	app_module.game = app_module.Mastermind(secret=(1, 2, 3, 4), mode="player")

	response = client.get("/game/distribution")
	payload = response.get_json()

	assert response.status_code == 200
	assert payload["candidate_count"] == 1296
	assert len(payload["distributions"]) == 3
	assert {"guess", "outcomes"} <= payload["distributions"][0].keys()
	assert all({"black", "white", "count", "probability"} <= outcome.keys()
			   for outcome in payload["distributions"][0]["outcomes"])


def test_algorithm_analysis_compares_entropy_and_minimax(client):
	app_module.game = app_module.Mastermind(secret=(1, 2, 3, 4), mode="player")

	response = client.get("/game/algorithm-analysis")
	payload = response.get_json()

	assert response.status_code == 200
	assert payload["n"] == 60
	assert payload["candidate_count"] == 1296
	assert payload["criteria_checked"] == [
		"entropy", "expected_elimination", "expected_remaining", "minimax_worst_case"
	]
	assert set(payload["algorithms"]) == {"entropy", "minimax"}
	for algorithm in payload["algorithms"].values():
		assert {"recommended_guess", "metrics", "distribution"} <= algorithm.keys()
		assert sum(item["count"] for item in algorithm["distribution"]) == 1296
		assert sum(item["probability"] for item in algorithm["distribution"]) == pytest.approx(100, abs=0.2)


def test_algorithm_analysis_recommends_unique_candidate(client):
	app_module.game = app_module.Mastermind(secret=(3, 5, 3, 4), mode="player")
	for guess in (
		[3, 4, 5, 6], [1, 2, 3, 4], [3, 3, 3, 3],
		[4, 4, 4, 4], [3, 5, 4, 3],
	):
		assert client.post("/guess", json={"guess": guess}).status_code == 200

	payload = client.get("/game/algorithm-analysis").get_json()

	assert payload["candidate_count"] == 1
	for algorithm in payload["algorithms"].values():
		assert algorithm["recommended_guess"] == [3, 5, 3, 4]
		assert algorithm["metrics"] == {
			"entropy_bits": 0,
			"expected_elimination_percent": 0,
			"expected_remaining": 1,
			"worst_case_remaining": 1,
		}
		assert algorithm["distribution"] == [{
			"black": 4,
			"white": 0,
			"count": 1,
			"probability": 100.0,
		}]


def test_guesses_consume_colour_stock_and_advice_respects_it(client):
	app_module.game = app_module.Mastermind(secret=(6, 6, 6, 6))
	for guess in ([1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 2, 2]):
		response = client.post("/guess", json={"guess": guess})
		assert response.status_code == 200

	advice = client.get("/game/advice").get_json()
	assert advice["colour_inventory"]["1"] == 0
	assert advice["total_remaining"] == 48
	assert all(1 not in option["guess"] for option in advice["recommendations"])

	blocked_guess = client.post("/guess", json={"guess": [1, 2, 3, 4]})
	assert blocked_guess.status_code == 409
	assert "Not enough pegs" in blocked_guess.get_json()["error"]


def test_player_secret_setup_keeps_guess_inventory_full(client):
	response = client.post("/new-game", json={
		"mode": "player",
		"secret": [1, 2, 3, 4],
	})

	assert response.status_code == 200
	assert response.get_json()["colour_inventory"] == {str(colour): 10 for colour in range(1, 7)}


def test_invalid_guess_returns_bad_request(client):
	response = client.post("/guess", json={"guess": [0, 7, 1]})

	assert response.status_code == 400
	assert "four values" not in response.get_json()["error"]


def test_statistics_and_solver_results(client):
	statistics_response = client.get("/statistics")
	solver_results_response = client.get("/solver-results")

	assert statistics_response.status_code == 200
	assert "solver_results" in statistics_response.get_json()
	assert solver_results_response.status_code == 200
	assert len(solver_results_response.get_json()) == 6


def test_statistics_includes_player_analytics(client):
	response = client.get("/statistics")

	assert response.status_code == 200
	assert {"games_played", "win_rate", "average_guesses"} <= response.get_json()["player_analytics"].keys()


def test_solver_run_returns_solution(client):
	response = client.post("/solver/run", json={"solver": "minimax"})

	assert response.status_code == 200
	assert response.get_json()["solved"] is True
