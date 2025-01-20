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

# 評価関数（角を避ける、終盤で強化）
def evaluate_board(board, stone):
    weight = [
        [10, 5, 5, 5, 5, 10],
        [5, 1, 2, 2, 1, 5],
        [5, 2, 0, 0, 2, 5],
        [5, 2, 0, 0, 2, 5],
        [5, 1, 2, 2, 1, 5],
        [10, 5, 5, 5, 5, 10]
    ]

    # 角を取らせないようにする（4隅を重要視）
    corner_weight = [
        [50, -10, -10, -10, -10, 50],
        [-10, -20, -20, -20, -20, -10],
        [-10, -20, -30, -30, -20, -10],
        [-10, -20, -30, -30, -20, -10],
        [-10, -20, -20, -20, -20, -10],
        [50, -10, -10, -10, -10, 50]
    ]

    score = 0
    for y in range(len(board)):
        for x in range(len(board[0])):
            if board[y][x] == stone:
                score += weight[y][x]
            elif board[y][x] == 3 - stone:
                score -= weight[y][x]

            # 角に石があると強く評価
            if board[y][x] == stone:
                score += corner_weight[y][x]
            elif board[y][x] == 3 - stone:
                score -= corner_weight[y][x]

    return score

# ミニマックス法
def minimax(board, stone, depth, maximizing_player, alpha=-math.inf, beta=math.inf):
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
        return min_eval

# weareteam AI クラス
class weareteam:

    def name(self):
        return "weareteam AI 🌷"

    def face(self):
        return "🌷"

    def place(self, board, stone):
        valid_moves = get_valid_moves(board, stone)
        if not valid_moves:
            return None

        best_move = None
        best_score = -math.inf

        for x, y in valid_moves:
            temp_board = apply_move(board, stone, x, y)
            score = minimax(temp_board, 3 - stone, depth=5, maximizing_player=False)

            if score > best_score:
                best_score = score
                best_move = (x, y)

        return best_move
