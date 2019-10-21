#!/usr/bin/python3
# -*- encoding: utf-8 -*-
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
from Board import Board
from Board import RejectedMove

# test the board state using "easy" notation
def test_BoardEasy():
    dominatorOffset = (0,-1) # Dominator is on the next cell to the right
    board = Board(dominatorOffset)
    try: #Easy mode
        print (board.performMove(['D2', 'D4']))             #d4
        print (board.performMove(['G8','F6']))              #Nf6
        print (board.performMove(['C2','C4']))              #c4
        print (board.performMove(['E7','E6']))              #e6
        print (board.performMove(['C4','C5']))              #c5
        print (board.performMove(['F8','D6']))              #Bd6
        print (board.performMove(['D1','A4']))              #Qa4
        print (board.performMove(['B7','B5']))              #b5
        print (board.performMove(['B5','C5','B6']))   #cxb6, En Passant
        print (board.performMove(['H8','E8','G8','F8']))    #0-0
        print (board.performMove(['B6','C7']))              #bxc7, Hidden eat
    except RejectedMove as e:
        print(e)
        pass
    print("---Final positions---")
    print (board.position())

# test the board state using "hard" notation
def test_BoardHard():
    dominatorOffset = (0,-1) # Dominator is on the next cell to the right
    board = Board(dominatorOffset)
    try: #Hard mode
        print(board.performMove(['D2','D3','D4','D5']))        #d4
        print(board.performMove(['G8','F7','F6']))              #Nf6
        print(board.performMove(['C2','C3','C4']))              #c4
        print(board.performMove(['E8','E7','E6']))              #e6
        print(board.performMove(['C4','C5']))              #c5 (putting C6 is an ambiguous move)
        print(board.performMove(['F8','D6', 'D7']))              #Bd6
        print(board.performMove(['D1', 'D2','A4','A5']))              #Qa4
        print(board.performMove(['B7','B5', 'B8','B6']))              #b5
        print(board.performMove(['B5','C5','B6', 'B7', 'C6']))   #cxb6, En Passant
        print(board.performMove(['H8','E8','G8','F8','H7','E7','G7','F7']))    #0-0
        print(board.performMove(['B6','C7','B7','C8']))              #bxc7, Hidden eat
    except RejectedMove as e:
        print(e)
        pass
    print("---Final positions---")
    print (board.position())

test_BoardHard()
test_BoardEasy()
