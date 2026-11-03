from flask import Flask
from flask import jsonify
from flask import request
from flask import send_from_directory
from pathlib import Path
from datetime import datetime, timezone
import json
import os

from backend.api.routes import API_ROUTES
from backend.api.schemas import GuessRequest, GuessResponse, NewGameResponse, SolverRequest
from backend.game.mastermind import Mastermind
from backend.services.solver_service import run_solver
from backend.services.game_advisor import get_algorithm_analysis, get_game_advice
from backend.services.statistics_service import get_benchmark_results, get_solver_results
from backend.database.db import (
    complete_game,
    create_game,
    get_active_game,
    get_game_analytics,
    initialize_database,
)

app = Flask(__name__)

GRAPHS_DIRECTORY = Path(__file__).resolve().parent / "results" / "graphs"
FRONTEND_DIRECTORY = Path(__file__).resolve().parent / "frontend"

initialize_database()


def restore_active_game():
    saved_game = get_active_game()
    if saved_game is None:
        return Mastermind(), None

    restored_game = Mastermind(
        secret=tuple(json.loads(saved_game["secret"])),
        mode=saved_game["mode"],
    )
    restored_game.history = json.loads(saved_game["guesses"])
    for entry in restored_game.history:
        for colour in entry["guess"]:
            restored_game.remaining_colour_counts[colour] -= 1
    restored_game.game_over = bool(saved_game["won"]) or (
        sum(restored_game.remaining_colour_counts.values()) < 4
    )
    return restored_game, saved_game["id"]


game, game_id = restore_active_game()


def utc_now():
    return datetime.now(timezone.utc).isoformat()


@app.after_request
def allow_frontend_requests(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response

@app.route("/")
def home():
    return send_from_directory(FRONTEND_DIRECTORY / "pages", "home.html")


@app.route("/pages/<path:filename>")
def frontend_page(filename):
    return send_from_directory(FRONTEND_DIRECTORY / "pages", filename)


@app.route("/css/<path:filename>")
def frontend_stylesheet(filename):
    return send_from_directory(FRONTEND_DIRECTORY / "css", filename)


@app.route("/js/<path:filename>")
def frontend_script(filename):
    return send_from_directory(FRONTEND_DIRECTORY / "js", filename)


@app.route("/health")
def health():
    return jsonify({
        "status": "ok"
    })


@app.route("/new-game", methods=["GET", "POST"])
def new_game():

    global game, game_id

    payload = request.get_json(silent=True) or {}
    mode = payload.get("mode", "computer")
    secret = payload.get("secret") if mode == "player" else None

    try:
        game = Mastermind(secret=secret, mode=mode)
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    game_id = create_game(game.mode, utc_now(), game.secret)

    return jsonify({
        **NewGameResponse("new game created", []).to_dict(),
        "mode": game.mode,
        "game_id": game_id,
        "colour_inventory": game.remaining_colour_counts,
    })


@app.route("/guess", methods=["POST"])
def guess():

    payload = request.get_json(silent=True) or {}
    submitted_guess = GuessRequest.from_payload(payload).guess

    if (
        not isinstance(submitted_guess, list)
        or len(submitted_guess) != 4
        or any(not isinstance(value, int) or not 1 <= value <= 6 for value in submitted_guess)
    ):
        return jsonify({
            "error": "Guess must contain four numbers from 1 to 6"
        }), 400

    try:
        black, white = game.guess(tuple(submitted_guess))
    except ValueError as error:
        return jsonify({"error": str(error)}), 409

    if game_id is not None:
        complete_game(
            game_id,
            utc_now() if game.game_over else None,
            len(game.history),
            game.game_over,
            json.dumps(game.history),
        )

    response = GuessResponse(
        black=black,
        white=white,
        won=black == 4,
        attempts=len(game.history),
        game_over=game.game_over,
        history=game.history,
    ).to_dict()
    response["colour_inventory"] = game.remaining_colour_counts
    return jsonify(response)


@app.route("/game/advice")
def game_advice():
    if game.game_over:
        return jsonify({
            "candidate_count": 0,
            "recommendations": [],
            "outcome_distributions": [],
            "colour_inventory": game.remaining_colour_counts,
            "total_remaining": sum(game.remaining_colour_counts.values()),
            "game_over": True,
            "solved": bool(game.history and game.history[-1]["black"] == 4),
        })

    try:
        advice = get_game_advice(game.history, game.remaining_colour_counts)
    except ValueError as error:
        return jsonify({"error": str(error)}), 409

    advice["game_over"] = False
    advice["outcome_distributions"] = [
        {
            "guess": recommendation["guess"],
            "outcomes": recommendation["distribution"],
        }
        for recommendation in advice["recommendations"]
    ]
    return jsonify(advice)


@app.route("/game/distribution")
def game_distribution():
    """Return only the predicted feedback distributions for recommended guesses."""
    response = game_advice()
    if response.status_code != 200:
        return response

    payload = response.get_json()
    return jsonify({
        "candidate_count": payload["candidate_count"],
        "distributions": payload["outcome_distributions"],
        "game_over": payload["game_over"],
    })


@app.route("/game/algorithm-analysis")
def game_algorithm_analysis():
    try:
        return jsonify(get_algorithm_analysis(
            game.history, game.remaining_colour_counts
        ))
    except ValueError as error:
        return jsonify({"error": str(error)}), 409


@app.route("/history")
def history():
    return jsonify({
        "history": game.history,
        "game_over": game.game_over
    })


@app.route("/solver/run", methods=["POST"])
def solver_run():
    payload = request.get_json(silent=True) or {}
    solver_name = SolverRequest.from_payload(payload).solver

    try:
        result = run_solver(solver_name, game.secret)
    except (TypeError, ValueError) as error:
        return jsonify({"error": str(error)}), 400

    return jsonify(result)


@app.route("/statistics")
def statistics():
    return jsonify({
        "results": get_benchmark_results(),
        "solver_results": get_solver_results(),
        "player_analytics": get_game_analytics(),
    })


@app.route("/graphs/<path:filename>")
def graph_file(filename):
    return send_from_directory(GRAPHS_DIRECTORY, filename)


@app.route("/solver-results")
def solver_results():
    return jsonify(get_solver_results())


@app.route("/player-analytics")
def player_analytics():
    return jsonify(get_game_analytics())


if __name__ == "__main__":
    app.run(
        debug=os.environ.get("FLASK_DEBUG", "").lower() == "1",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "5001")),
    )