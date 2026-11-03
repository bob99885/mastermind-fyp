"""Application service for managing a single Mastermind game."""

from backend.game.mastermind import Mastermind


class GameService:
	def __init__(self, game=None):
		self.game = game or Mastermind()

	def reset(self):
		self.game = Mastermind()
		return self.game

	def submit_guess(self, guess):
		return self.game.guess(tuple(guess))

	def history(self):
		return self.game.history
