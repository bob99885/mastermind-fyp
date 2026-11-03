from dataclasses import dataclass

@dataclass
class GameResult:
    solver: str
    guesses: int
    runtime: float


@dataclass
class PlayerAnalytics:
    games_played: int
    completed_games: int
    wins: int = 0
    win_rate: float = 0
    average_guesses: float | None = None
    fastest_win: int | None = None
    most_common_opening: str | None = None
    most_used_colour: str | None = None