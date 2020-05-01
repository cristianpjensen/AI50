"""
Tic Tac Toe Player
"""

import math
import copy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    count = 0

    for row in board:
        for value in row:
            if value == X or value == O:
                count += 1

    if count % 2 == 0:
        return X
    else:
        return O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    actions = set()

    for i in range(len(board)):
        for j in range(len(board[i])):
            if board[i][j] == EMPTY:
                actions.add((i,j))

    return actions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """

    # Make a deep copy
    resulting_board = copy.deepcopy(board)

    row = list(action)[0]
    column = list(action)[1]

    if resulting_board[row][column] == EMPTY:
        resulting_board[row][column] = player(board)
    else:
        raise ValueError

    return resulting_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    if utility(board) == 1:
        return X
    elif utility(board) == -1:
        return O
    else:
        return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) != None:
        return True

    items = set()

    for row in board:
        for item in row:
            items.add(item)

    if EMPTY not in items:
        return True

    return False


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    # Check for horizontal wins.
    for row in board:
        if len(set(row)) == 1 and EMPTY not in set(row):
            if row[0] == X:
                return 1
            elif row[0] == O:
                return -1

    # Check for vertical wins.
    for column in range(len(board)):
        items = set()
        for row in range(3):
            items.add(board[row][column])
        if len(items) == 1 and EMPTY not in items:
            winner = items.pop()
            if winner == X:
                return 1
            elif winner == O:
                return -1

    # Top-left to bottom-right.
    items = set()
    for row in range(len(board)):
        column = row
        items.add(board[row][column])
    if len(items) == 1 and EMPTY not in items:
        winner = items.pop()
        if winner == X:
            return 1
        elif winner == O:
            return -1

    # Bottom-left to top-right.
    items = set()
    for row in range(len(board)):
        if row == 0:
            column = 2
        elif row == 1:
            column = 1
        elif row == 2:
            column = 0
        items.add(board[row][column])
    if len(items) == 1 and EMPTY not in items:
        winner = items.pop()
        if winner == X:
            return 1
        elif winner == O:
            return -1

    return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        return None

    turn = player(board)

    # MAX
    if turn == X:
        for action in actions(board):
            if min_value(result(board, action)) == 1:
                return action
        for action in actions(board):
            if min_value(result(board, action)) == 0:
                return action
        for action in actions(board):
            if min_value(result(board, action)) == -1:
                return action

    # MIN
    elif turn == O:
        for action in actions(board):
            if max_value(result(board, action)) == -1:
                return action
        for action in actions(board):
            if max_value(result(board, action)) == 0:
                return action
        for action in actions(board):
            if max_value(result(board, action)) == 1:
                return action


def max_value(board):
    if terminal(board):
        return utility(board)

    v = -math.inf

    for action in actions(board):
        v = max(v, min_value(result(board, action)))
    return v


def min_value(board):
    if terminal(board):
        return utility(board)

    v = +math.inf

    for action in actions(board):
        v = min(v, max_value(result(board, action)))
    return v
