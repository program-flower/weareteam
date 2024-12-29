import math
import random
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor

BLACK = 1
WHITE = 2

board = [
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
        [0, 0, 1, 2, 0, 0],
        [0, 0, 2, 1, 0, 0],
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
]

# 評価表（静的な位置の価値）
EVALUATION_TABLE = [
    [150, -20, 10, 10, -20, 150],
    [-20, -50, -2, -2, -50, -20],
    [ 10,  -2,  0,  0,  -2,  10],
    [ 10,  -2,  0,  0,  -2,  10],
    [-20, -50, -2, -2, -50, -20],
    [150, -20, 10, 10, -20, 150],
]

# 置換表
transposition_table = {}

def can_place_x_y(board, stone, x, y):
    if board[y][x] != 0:
        return False

    opponent = 3 - stone
    directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    flip_count = 0

    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        found_opponent = False
        temp_flip_count = 0

        while 0 <= nx < len(board[0]) and 0 <= ny < len(board) and board[ny][nx] == opponent:
            nx += dx
            ny += dy
            found_opponent = True
            temp_flip_count += 1

        if found_opponent and 0 <= nx < len(board[0]) and 0 <= ny < len(board) and board[ny][nx] == stone:
            flip_count += temp_flip_count

    return flip_count if flip_count > 0 else False

def can_place(board, stone):
    for y in range(len(board)):
        for x in range(len(board[0])):
            if can_place_x_y(board, stone, x, y):
                return True
    return False

def evaluate_board(board, stone):
    score = 0
    for y in range(len(board)):
        for x in range(len(board[0])):
            if board[y][x] == stone:
                score += EVALUATION_TABLE[y][x]
            elif board[y][x] == (3 - stone):
                score -= EVALUATION_TABLE[y][x]

    # 安定石の評価を追加
    def is_stable(x, y):
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < len(board[0]) and 0 <= ny < len(board):
                if board[ny][nx] == 0:
                    return False
        return True

    for y in range(len(board)):
        for x in range(len(board[0])):
            if board[y][x] == stone and is_stable(x, y):
                score += 100
            elif board[y][x] == (3 - stone) and is_stable(x, y):
                score -= 100

    return score

def get_valid_moves(board, stone):
    moves = []
    for y in range(len(board)):
        for x in range(len(board[0])):
            if can_place_x_y(board, stone, x, y):
                moves.append((x, y))
    return moves

def apply_move(board, stone, x, y):
    new_board = [row[:] for row in board]
    new_board[y][x] = stone
    opponent = 3 - stone
    directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        stones_to_flip = []

        while 0 <= nx < len(board[0]) and 0 <= ny < len(board):
            if new_board[ny][nx] == opponent:
                stones_to_flip.append((nx, ny))
            elif new_board[ny][nx] == stone:
                for fx, fy in stones_to_flip:
                    new_board[fy][fx] = stone
                break
            else:
                break

            nx += dx
            ny += dy

    return new_board

def mtdf(board, stone, depth, first_guess):
    g = first_guess
    upper_bound = math.inf
    lower_bound = -math.inf

    while lower_bound < upper_bound:
        beta = g if g == lower_bound else (g + 1)
        g, _ = minimax(board, stone, depth, True, beta - 1, beta)
        if g < beta:
            upper_bound = g
        else:
            lower_bound = g

    return g

def minimax(board, stone, depth, maximizing, alpha=-math.inf, beta=math.inf):
    board_key = tuple(tuple(row) for row in board)
    if board_key in transposition_table:
        return transposition_table[board_key]

    if depth == 0 or not can_place(board, stone):
        score = evaluate_board(board, stone)
        transposition_table[board_key] = (score, None)
        return score, None

    valid_moves = get_valid_moves(board, stone)
    best_move = None

    if maximizing:
        max_eval = -math.inf
        for x, y in valid_moves:
            new_board = apply_move(board, stone, x, y)
            eval, _ = minimax(new_board, 3 - stone, depth - 1, False, alpha, beta)
            if eval > max_eval:
                max_eval = eval
                best_move = (x, y)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        transposition_table[board_key] = (max_eval, best_move)
        return max_eval, best_move
    else:
        min_eval = math.inf
        for x, y in valid_moves:
            new_board = apply_move(board, stone, x, y)
            eval, _ = minimax(new_board, 3 - stone, depth - 1, True, alpha, beta)
            if eval < min_eval:
                min_eval = eval
                best_move = (x, y)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        transposition_table[board_key] = (min_eval, best_move)
        return min_eval, best_move

def best_place(board, stone):
    empty_cells = sum(row.count(0) for row in board)
    if empty_cells > 20:
        first_guess = 0
        move = mtdf(board, stone, depth=4, first_guess=first_guess)
        return move
    elif empty_cells > 10:
        first_guess = 0
        move = mtdf(board, stone, depth=8, first_guess=first_guess)
        return move
    else:
        valid_moves = get_valid_moves(board, stone)
        with ThreadPoolExecutor() as executor:
            scores = list(executor.map(lambda mv: evaluate_board(apply_move(board, stone, mv[0], mv[1]), stone), valid_moves))
        best_index = scores.index(max(scores))
        return valid_moves[best_index]

class WeareteamAI(object):
    def face(self):
        return "🦁"

    def place(self, board, stone):
        x, y = best_place(board, stone)
        return x, y
