import math
import random
from functools import lru_cache

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
    [100, -20, 10, 10, -20, 100],
    [-20, -50, -2, -2, -50, -20],
    [ 10,  -2,  0,  0,  -2,  10],
    [ 10,  -2,  0,  0,  -2,  10],
    [-20, -50, -2, -2, -50, -20],
    [100, -20, 10, 10, -20, 100],
]

def can_place_x_y(board, stone, x, y):
    """
    石を置けるかどうかを調べる関数。
    board: 2次元配列のオセロボード
    x, y: 石を置きたい座標 (0-indexed)
    stone: 現在のプレイヤーの石 (1: 黒, 2: 白)
    return: 置けるなら True, 置けないなら False
    """
    if board[y][x] != 0:
        return False  # 既に石がある場合は置けない

    opponent = 3 - stone  # 相手の石 (1なら2、2なら1)
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
            flip_count += temp_flip_count  # 返せる石の数をカウント

    return flip_count if flip_count > 0 else False

def can_place(board, stone):
    """
    石を置ける場所を調べる関数。
    board: 2次元配列のオセロボード
    stone: 現在のプレイヤーの石 (1: 黒, 2: 白)
    """
    for y in range(len(board)):
        for x in range(len(board[0])):
            if can_place_x_y(board, stone, x, y):
                return True
    return False

def evaluate_board(board, stone):
    """
    現在のボード状態を評価する関数。
    board: 2次元配列のオセロボード
    stone: 評価するプレイヤーの石 (1: 黒, 2: 白)
    return: ボードの評価値
    """
    score = 0
    for y in range(len(board)):
        for x in range(len(board[0])):
            if board[y][x] == stone:
                score += EVALUATION_TABLE[y][x]
            elif board[y][x] == (3 - stone):
                score -= EVALUATION_TABLE[y][x]

    # 安定石の評価
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
                score += 50
            elif board[y][x] == (3 - stone) and is_stable(x, y):
                score -= 50

    return score

def get_valid_moves(board, stone):
    """
    有効な手をすべて取得する関数。
    """
    moves = []
    for y in range(len(board)):
        for x in range(len(board[0])):
            if can_place_x_y(board, stone, x, y):
                moves.append((x, y))
    return moves

def apply_move(board, stone, x, y):
    """
    石を置いた結果を反映した新しいボードを返す。
    """
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

def minimax(board, stone, depth, maximizing, alpha=-math.inf, beta=math.inf):
    """
    ミニマックス法を用いて最善手を計算する。
    アルファベータ枝刈りを導入。
    """
    if depth == 0 or not can_place(board, stone):
        return evaluate_board(board, stone), None

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
        return min_eval, best_move

@lru_cache(maxsize=None)
def cached_minimax(board_tuple, stone, depth, maximizing):
    """
    キャッシュ付きのミニマックス計算。
    """
    board = [list(row) for row in board_tuple]
    return minimax(board, stone, depth, maximizing)

def check_forced_win(board, stone, depth):
    """
    必勝読みを行う関数。
    現在の手番からdepth手以内に勝利できるかを探索する。
    """
    if depth == 0 or not can_place(board, stone):
        return evaluate_board(board, stone) > 0, None

    valid_moves = get_valid_moves(board, stone)
    for x, y in valid_moves:
        new_board = apply_move(board, stone, x, y)
        opponent_can_win, _ = check_forced_win(new_board, 3 - stone, depth - 1)
        if not opponent_can_win:  # 相手に必勝手がない場合
            return True, (x, y)

    return False, None

def full_search(board, stone):
    """
    終盤で完全読みを行い最善手を計算する。
    """
    valid_moves = get_valid_moves(board, stone)
    best_move = None
    best_score = -math.inf

    for x, y in valid_moves:
        new_board = apply_move(board, stone, x, y)
        score = evaluate_board(new_board, stone)
        if score > best_score:
            best_score = score
            best_move = (x, y)

    return best_move

def best_place(board, stone):
    """
    石を最善手に基づいて置く関数。
    board: 2次元配列のオセロボード
    stone: 現在のプレイヤーの石 (1: 黒, 2: 白)
    """
    empty_cells = sum(row.count(0) for row in board)
    if empty_cells > 20:  # 序盤では探索深さを16に設定
        _, move = minimax(board, stone, depth=16, maximizing=True)
        return move
    elif empty_cells > 10:  # 中盤では探索深さを32に設定
        _, move = minimax(board, stone, depth=32, maximizing=True)
        return move
    else:  # 終盤
        # 必勝読みを優先
        can_win, move = check_forced_win(board, stone, depth=6)
        if can_win:
            return move
        # 必勝手がなければ完全読み
        return full_search(board, stone)

class WeareteamAI(object):
    def face(self):
        return "🦁"

    def place(self, board, stone):
        x, y = best_place(board, stone)
        return x, y
