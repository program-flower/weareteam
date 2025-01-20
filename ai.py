import math

BLACK = 1
WHITE = 2

# 初期の盤面
board = [
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 1, 2, 0, 0],
    [0, 0, 2, 1, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
]

# 石を置く
def apply_move(board, stone, x, y):
    new_board = [row[:] for row in board]
    new_board[y][x] = stone

    opponent = 3 - stone
    directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        stones_to_flip = []

        while 0 <= nx < len(new_board[0]) and 0 <= ny < len(new_board) and new_board[ny][nx] == opponent:
            stones_to_flip.append((nx, ny))
            nx += dx
            ny += dy

        if stones_to_flip and 0 <= nx < len(new_board[0]) and 0 <= ny < len(new_board) and new_board[ny][nx] == stone:
            for flip_x, flip_y in stones_to_flip:
                new_board[flip_y][flip_x] = stone

    return new_board

# 有効な手を取得
def get_valid_moves(board, stone):
    valid_moves = []
    for y in range(len(board)):
        for x in range(len(board[0])):
            if can_place_x_y(board, stone, x, y):
                valid_moves.append((x, y))
    return valid_moves

# 手を置けるかチェック
def can_place_x_y(board, stone, x, y):
    if board[y][x] != 0:
        return False

    opponent = 3 - stone
    directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        found_opponent = False

        while 0 <= nx < len(board[0]) and 0 <= ny < len(board) and board[ny][nx] == opponent:
            nx += dx
            ny += dy
            found_opponent = True

        if found_opponent and 0 <= nx < len(board[0]) and 0 <= ny < len(board) and board[ny][nx] == stone:
            return True

    return False

# 安定した石を数える
def count_stable_stones(board, stone):
    stable = 0
    directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    for y in range(len(board)):
        for x in range(len(board[0])):
            if board[y][x] == stone:
                is_stable = True
                for dx, dy in directions:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < len(board[0]) and 0 <= ny < len(board) and board[ny][nx] == 0:
                        is_stable = False
                        break
                if is_stable:
                    stable += 1
    return stable

# 評価関数
def evaluate_board(board, stone):
    weight = [
        [10, -3,  2,  2, -3, 10],
        [-3, -5, -1, -1, -5, -3],
        [ 2, -1,  1,  1, -1,  2],
        [ 2, -1,  1,  1, -1,  2],
        [-3, -5, -1, -1, -5, -3],
        [10, -3,  2,  2, -3, 10]
    ]
    score = 0
    for y in range(len(board)):
        for x in range(len(board[0])):
            if board[y][x] == stone:
                score += weight[y][x]
    score += count_stable_stones(board, stone) * 5
    return score

# ミニマックス法
cache = {}

def minimax(board, stone, depth, maximizing_player, alpha=-math.inf, beta=math.inf):
    board_tuple = tuple(tuple(row) for row in board)
    if (board_tuple, stone, depth, maximizing_player) in cache:
        return cache[(board_tuple, stone, depth, maximizing_player)]

    valid_moves = get_valid_moves(board, stone)

    # 終端条件: 深さ0またはこれ以上石を置けない場合
    if depth == 0 or not valid_moves:
        return evaluate_board(board, stone)

    if maximizing_player:
        max_eval = -math.inf
        for x, y in valid_moves:
            new_board = apply_move(board, stone, x, y)
            eval = minimax(new_board, 3 - stone, depth - 1, False, alpha, beta)
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break  # βカット
        cache[(board_tuple, stone, depth, maximizing_player)] = max_eval
        return max_eval
    else:
        min_eval = math.inf
        for x, y in valid_moves:
            new_board = apply_move(board, stone, x, y)
            eval = minimax(new_board, 3 - stone, depth - 1, True, alpha, beta)
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break  # αカット
        cache[(board_tuple, stone, depth, maximizing_player)] = min_eval
        return min_eval

# tulip クラス
class tulip:

    def name(self):
        return "tulip"

    def face(self):
        return "🌷"

    def place(self, board, stone):
        valid_moves = get_valid_moves(board, stone)
        if not valid_moves:
            return None

        best_move = None
        best_score = -math.inf

        # 残りの手数に応じて探索深度を動的に変更
        remaining_moves = sum(row.count(0) for row in board)

        if remaining_moves <= 10:
            depth = remaining_moves  # 終盤では完全読み
        else:
            depth = 6 if remaining_moves > 15 else 8

        for x, y in valid_moves:
            temp_board = apply_move(board, stone, x, y)
            score = minimax(temp_board, 3 - stone, depth=depth, maximizing_player=False)

            if score > best_score:
                best_score = score
                best_move = (x, y)

        return best_move
