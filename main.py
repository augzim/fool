#!/usr/bin/env python3


from config import CONFIG
from game import FoolCardGame
from server import Server


if __name__ == '__main__':
    with Server('localhost', CONFIG['PORT']) as server:
        game = FoolCardGame(server)
        game.play()
