import sqlite3
import json
from pathlib import Path

DATABASE_NAME = Path(__file__).resolve().parents[2] / "mastermind.db"

def get_connection():
    connection = sqlite3.connect(DATABASE_NAME)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS games (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mode TEXT NOT NULL,
                started_at TEXT NOT NULL,
                secret TEXT,
                completed_at TEXT,
                attempts INTEGER NOT NULL DEFAULT 0,
                won INTEGER NOT NULL DEFAULT 0,
                guesses TEXT NOT NULL DEFAULT '[]'
            )
        """)
        columns = {
            row["name"]
            for row in connection.execute("PRAGMA table_info(games)").fetchall()
        }
        if "secret" not in columns:
            connection.execute("ALTER TABLE games ADD COLUMN secret TEXT")


def create_game(mode, started_at, secret):
    with get_connection() as connection:
        cursor = connection.execute(
            "INSERT INTO games (mode, started_at, secret) VALUES (?, ?, ?)",
            (mode, started_at, json.dumps(list(secret))),
        )
        return cursor.lastrowid


def get_active_game():
    with get_connection() as connection:
        return connection.execute(
            """SELECT * FROM games
            WHERE completed_at IS NULL AND secret IS NOT NULL
            ORDER BY id DESC LIMIT 1"""
        ).fetchone()


def complete_game(game_id, completed_at, attempts, won, guesses):
    with get_connection() as connection:
        connection.execute(
            """UPDATE games
            SET completed_at = ?, attempts = ?, won = ?, guesses = ?
            WHERE id = ?""",
            (completed_at, attempts, int(won), guesses, game_id),
        )


def get_game_analytics():
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT * FROM games WHERE mode IN ('computer', 'player') ORDER BY id"
        ).fetchall()

    completed = [row for row in rows if row["won"]]
    attempts = [row["attempts"] for row in completed]
    first_guesses = []
    colour_counts = {}
    for row in rows:
        guesses = json.loads(row["guesses"])
        if guesses:
            first_guesses.append("".join(str(value) for value in guesses[0]["guess"]))
        for entry in guesses:
            for colour in entry["guess"]:
                colour_counts[str(colour)] = colour_counts.get(str(colour), 0) + 1

    return {
        "games_played": len(rows),
        "completed_games": len(completed),
        "wins": len(completed),
        "win_rate": round(len(completed) / len(rows) * 100, 1) if rows else 0,
        "average_guesses": round(sum(attempts) / len(attempts), 2) if attempts else None,
        "fastest_win": min(attempts) if attempts else None,
        "most_common_opening": max(set(first_guesses), key=first_guesses.count) if first_guesses else None,
        "most_used_colour": max(colour_counts, key=colour_counts.get) if colour_counts else None,
    }