import numpy as np
import copy

# 定数
EMPTY, BLACK, WHITE = 0, 1, 2
DIRECTIONS = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)]

class OthelloAI:
    def __init__(self, max_depth=4):
        self.max_depth = max_depth

    def evaluate(self, board, player):
        # 評価関数の改良
        WEIGHTS = np.array([
            [100, -20, 10,  5,  5, 10, -20, 100],
            [-20, -50, -2, -2, -2, -2, -50, -20],
            [10,  -2,  -1, -1, -1, -1,  -2,  10],
            [5,   -2,  -1,  0,  0, -1,  -2,   5],
            [5,   -2,  -1,  0,  0, -1,  -2,   5],
            [10,  -2,  -1, -1, -1, -1,  -2,  10],
            [-20, -50, -2, -2, -2, -2, -50, -20],
            [100, -20, 10,  5,  5, 10, -20, 100]
        ])
        score = 0
        for y in range(8):
            for x in range(8):
                if board[y][x] == player:
                    score += WEIGHTS[y][x]
                elif board[y][x] == 3 - player:
                    score -= WEIGHTS[y][x]
        return score

    def is_valid_move(self, board, x, y, player):
        if board[y][x] != EMPTY:
            return False
        for dx, dy in DIRECTIONS:
            nx, ny = x + dx, y + dy
            has_opponent = False
            while 0 <= nx < 8 and 0 <= ny < 8:
                if board[ny][nx] == 3 - player:
                    has_opponent = True
                elif board[ny][nx] == player:
                    if has_opponent:
                        return True
                    break
                else:
                    break
                nx += dx
                ny += dy
        return False

    def get_valid_moves(self, board, player):
        return [(x, y) for y in range(8) for x in range(8) if self.is_valid_move(board, x, y, player)]

    def make_move(self, board, x, y, player):
        new_board = copy.deepcopy(board)
        new_board[y][x] = player
        for dx, dy in DIRECTIONS:
            nx, ny = x + dx, y + dy
            flips = []
            while 0 <= nx < 8 and 0 <= ny < 8:
                if new_board[ny][nx] == 3 - player:
                    flips.append((nx, ny))
                elif new_board[ny][nx] == player:
                    for fx, fy in flips:
                        new_board[fy][fx] = player
                    break
                else:
                    break
                nx += dx
                ny += dy
        return new_board

    def minimax(self, board, depth, alpha, beta, maximizing, player):
        opponent = 3 - player
        if depth == 0 or not self.get_valid_moves(board, player):
            return self.evaluate(board, player)

        if maximizing:
            max_eval = float('-inf')
            for move in self.get_valid_moves(board, player):
                new_board = self.make_move(board, move[0], move[1], player)
                eval = self.minimax(new_board, depth - 1, alpha, beta, False, player)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for move in self.get_valid_moves(board, opponent):
                new_board = self.make_move(board, move[0], move[1], opponent)
                eval = self.minimax(new_board, depth - 1, alpha, beta, True, player)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval

    def find_best_move(self, board, player):
        best_move = None
        best_value = float('-inf')
        for move in self.get_valid_moves(board, player):
            new_board = self.make_move(board, move[0], move[1], player)
            move_value = self.minimax(new_board, self.max_depth - 1, float('-inf'), float('inf'), False, player)
            if move_value > best_value:
                best_value = move_value
                best_move = move
        return best_move

# テスト用の初期ボード
initial_board = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 2, 1, 0, 0, 0],
    [0, 0, 0, 1, 2, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0]
]

# AIを実行
ai = OthelloAI(max_depth=4)
best_move = ai.find_best_move(initial_board, BLACK)
print(f"AIの最善手: {best_move}")
