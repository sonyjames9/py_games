"""
Represents a round of the game, storing info like
word, time, skips, drawing player and more
"""
import time as t
from _thread import *
# from game import Game
from chat import Chat


class Round(object):
    def __init__(self, word, player_drawing, game):
        """
        init object
        :param word:
        :param player_drawing:
        """
        self.players = None
        self.scores = None
        self.game = game
        self.word = word
        self.player_drawing = player_drawing
        self.player_guessed = []
        self.skips = 0
        self.time = 75
        self.game = game
        self.player_scores = {player: 0 for player in self.game.players}
        self.chat = Chat(self)
        start_new_thread(self.time_thread(), ())

    def skip(self, player):
        """
        Returns true if round threshold met
        :return: bool
        """
        self.skips += 1
        if self.skips > len(self.game.players) - 2:
            self.skips = 0
            return True
        return False

    def get_scores(self):
        """
        : returns all the player scores
        """
        return self.player_scores

    def get_score(self, player):
        """
        gets a specific player scores
        :param player: Player
        :return: int
        """
        if player in self.player_scores:
            return self.player_scores[player]
        else:
            raise Exception("Player not in score list")

    def time_thread(self):
        """
        Runs in thread to keep track of time
        :return: None
        """
        while self.time > 0:
            t.sleep(1)
            self.time -= 1
        self.end_round("Time is up")

    def guess(self, player, wrd):
        """
        returns bool if player got guess correct
        :param player:
        :param wrd:
        :return:
        """
        correct = wrd == self.word
        if correct:
            self.player_guessed.append(player)
        # TODO implement scoring system here

    def player_left(self, player):
        """
        removes player that left from scores and list
        :param player:
        :return: None
        """
        # might not be able to use player as key in dict
        if player in self.player_scores:
            del self.player_scores[player]

        if player in self.player_guessed:
            self.player_guessed.remove(player)

        if player == self.player_drawing:
            self.end_round("Drawing player left")

    def end_round(self, msg):
        for player in self.game.players:
            player.update_score(self.player_scores[player])
        self.game.round_ended()