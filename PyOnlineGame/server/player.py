"""
Represents player on server side
"""

from game import Game

class Player(object) :
    def __init__(self, ip, name):
        """
        init the player object
        :param ip: str
        :param name: str
        """
        self.game = None
        self.ip = ip
        self.name = name
        self.score = 0

    def set_game(self, game):
        """
        sets the players game association
        :param game: Game
        :return: None
        """
        self.game = game

    def update_score(self, x):
        """
        updates a player score
        :param x: int
        :return: None
        """
        self.score += x

    def guess(self, wrd):
        """
        makes a player guess
        :param wrd: str
        :return: bool
        """
        self.game.player_guess(self, wrd)

    def disconnect(self):
        """
        call to disconnect player
        :return: None
        """
        self.game.player_disconnected(self)

    def get_ip(self):
        """
        gets player ip address
        :return: str
        """
        return self.ip

    def get_name(self):
        """
        get player name
        :return: str
        """
        return self.name

    def get_score(self):
        """
        get player score
        :return: int
        """
        return self.score
