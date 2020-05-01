import tictactoe as ttt

X = "X"
O = "O"
EMPTY = None


board = [[O, EMPTY, EMPTY],
         [O, EMPTY, EMPTY],
         [EMPTY, EMPTY, O]]

print(ttt.winner(board))