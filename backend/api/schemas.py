"""Typed request and response shapes used by the Flask API."""

from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class GuessRequest:
	guess: list[int]

	@classmethod
	def from_payload(cls, payload: dict[str, Any]) -> "GuessRequest":
		return cls(guess=payload.get("guess"))


@dataclass
class GuessResponse:
	black: int
	white: int
	won: bool = False
	attempts: int = 0
	game_over: bool = False
	history: list[dict[str, Any]] | None = None

	def to_dict(self) -> dict[str, Any]:
		return asdict(self)


@dataclass
class NewGameResponse:
	message: str
	history: list[dict[str, Any]] | None = None

	def to_dict(self) -> dict[str, Any]:
		return asdict(self)


@dataclass
class SolverRequest:
	solver: str

	@classmethod
	def from_payload(cls, payload: dict[str, Any]) -> "SolverRequest":
		return cls(solver=payload.get("solver", "random"))


@dataclass
class SolverResponse:
	solver: str
	guesses: int
	solved: bool

	def to_dict(self) -> dict[str, Any]:
		return asdict(self)
