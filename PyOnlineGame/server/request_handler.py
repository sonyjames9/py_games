"""
Main thread
Handles all the connections, creating new games
and requests from the client(s)
"""

import socket
import threading
import time
from player import Player
from game import Game
from queue import Queue
import json


class Server(object):
    PLAYERS = 8

    def __init__(self):
        self.connection_queue = []
        self.game_id = 0

    def player_thread(self, conn, player):
        """
        handles in game communication between clients
        :param conn: connection object
        :param ip: str
        :param name: str
        :return: None
        """

        """
        
        """
        while True:
            try:
                # Receive request
                try:
                    data = conn.recv(1024)
                    # print("REPR")
                    # print(data)
                    # data = json.loads(data.decode("utf-8"))
                    data = data.decode('utf-8')
                    # print("Decode byte")
                    # print(data)
                    data = json.loads(data)
                    # print("REPR")
                    # data = json.load(data)
                    # print("Type" + str(type(data)))
                    # print("Keys : " + str(data.keys()))
                    # print("Values : " + str(data.values()))
                    print("[LOG] Received data : ", data)
                except Exception as err:
                    print("[EXCEPTION ] : "+str(err))
                    break
                # Player is not a part of game
                keys = [int(key) for key in data.keys()]
                send_msg = {key: [] for key in keys}
                last_board = None

                for key in keys:
                    if key == '-1':  # Get game
                        if player.game:
                            send = {player.get_name(): player.get_score() for player in player.game.players}
                            send_msg[-1] = send
                        else:
                            send_msg[-1] = []
                    if player.game:
                        if key == 0:  # Guess
                            print(data[0])
                            correct = player.game.player_guess(player, data['0'][0])
                            send_msg[0] = correct
                        elif key == 1:  # Skip
                            print("HERE")
                            skip = player.game.skip()
                            print(skip)
                            send_msg[1] = skip
                        elif key == 2:  # Get chat
                            content = player.game.round.chat.get_chat()
                            send_msg[2] = content
                        elif key == 3:  # Get board
                            get_board = player.game.board.get_board()
                            send_msg[3] = get_board
                        elif key == 4:  # Get score
                            scores = player.game.get_player_scores()
                            send_msg[4] = scores
                        elif key == 5:  # Get round
                            rnd = player.game.round_count
                            send_msg[5] = rnd
                        elif key == 6:  # Get word
                            word = player.game.round.word
                            send_msg[6] = word
                        elif key == 7:  # Get skips
                            skips = player.game.round.skips
                            send_msg[7] = skips
                        elif key == 8:  # Update board
                            x, y, color = data['8'][:3]
                            player.game.update_board(x, y, color)
                        elif key == 9:  # Get round time
                            time_val = player.game.round.time
                            send_msg[9] = time_val
                        else:
                            raise Exception("Not a valid request")

                send_msg = json.dumps(send_msg)
                conn.sendall(json.dumps(send_msg).encode())
            except Exception() as err:
                print(f"[Exception] {player.get_name()}:", err)
                break

        print(f"[DISCONNECT] {player.name} DISCONNECTED")
        # player.game.player_disconnected(player)
        conn.close()

    def handle_queue(self, player):
        """
        adds player to queue and creates new game if enough players
        :param player:
        :return:
        """
        game = None
        self.connection_queue.append(player)
        if len(self.connection_queue) >= self.PLAYERS:
            game = Game(self.game_id, self.connection_queue[:])

        for player_p in self.connection_queue:
            player_p.set_game(game)

        self.game_id += 1
        self.connection_queue = []
        print(f"[GAME] Game {self.game_id - 1} started...")

    def authentication(self, conn, addr):
        """
        authentication here
        :param ip: str
        :return: None
        """
        try:
            data = conn.recv(1024)
            name = str(data.decode())
            print(name)
            if not name:
                raise Exception("No name received")

            conn.sendall("1".encode())

            player = Player(addr, name)
            self.handle_queue(player)
            thread = threading.Thread(target=self.player_thread, args=(conn, player))
            thread.start()
        except Exception as e:
            print("[EXCEPTION]", e)
            conn.close()

    def connection_thread(self):
        server = ""
        port = 5555

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            sock.bind((server, port))
        except socket.error as e:
            str(e)

        sock.listen(1)
        print("Waiting for connection, Server started")

        while True:
            conn, addr = sock.accept()
            print("[CONNECT] New connection")

            self.authentication(conn, addr)


if __name__ == "__main__":
    server_object = Server()
    thread = threading.Thread(target=server_object.connection_thread)
    thread.start()
