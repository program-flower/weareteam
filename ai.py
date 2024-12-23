import random
import time
import math
from functools import lru_cache
import multiprocessing

# 初期化
ZOBRIST_TABLE = [[[random.randint(0, 2**64 - 1) for _ in range(2)] for _ in range(8)] for _ in range(8)]

@lru_cache(maxsize=None)
def zobrist_hash(board, player):
    h = 0
    for i in range(8):
        for j in range(8):
            if board[i][j] == '●':
                h ^= ZOBRIST_TABLE[i][j][0]
            elif board[i][j] == '○':
                h ^= ZOBRIST_TABLE[i][j][1]
    if player == '○':
        h ^= random.randint(0, 2**64 - 1)
    return h

def initialize_board():
    board = [['.' for _ in range(8)] for _ in range(8)]
    board[3][3] = '○'
    board[3][4] = '●'
    board[4][3] = '●'
    board[4][4] = '○'
    return board

def print_board(board):
    print("   a b c d e f g h")
    for i in range(8):
        row = f"{i + 1:>2} "
        for j in range(8):
            row += board[i][j] + ' '
        print(row)

def is_valid_move(board, row, col, player):
    if board[row][col] != '.':
        return False

    opponent = '●' if player == '○' else '○'
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    for dr, dc in directions:
        r, c = row + dr, col + dc
        has_opponent_between = False

        while 0 <= r < 8 and 0 <= c < 8 and board[r][c] == opponent:
            r += dr
            c += dc
            has_opponent_between = True

        if has_opponent_between and 0 <= r < 8 and 0 <= c < 8 and board[r][c] == player:
            return True

    return False

def get_valid_moves(board, player):
    valid_moves = []
    for row in range(8):
        for col in range(8):
            if is_valid_move(board, row, col, player):
                valid_moves.append((row, col))
    return valid_moves

def make_move(board, row, col, player):
    board[row][col] = player
    opponent = '●' if player == '○' else '○'
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    for dr, dc in directions:
        r, c = row + dr, col + dc
        stones_to_flip = []

        while 0 <= r < 8 and 0 <= c < 8 and board[r][c] == opponent:
            stones_to_flip.append((r, c))
            r += dr
            c += dc

        if 0 <= r < 8 and 0 <= c < 8 and board[r][c] == player:
            for rr, cc in stones_to_flip:
                board[rr][cc] = player

def evaluate_board(board, player):
    opponent = '●' if player == '○' else '○'
    weights = [
        [100, -20, 10,  5,  5, 10, -20, 100],
        [-20, -50, -2, -2, -2, -2, -50, -20],
        [ 10,  -2,  1,  1,  1,  1,  -2,  10],
        [  5,  -2,  1,  0,  0,  1,  -2,   5],
        [  5,  -2,  1,  0,  0,  1,  -2,   5],
        [ 10,  -2,  1,  1,  1,  1,  -2,  10],
        [-20, -50, -2, -2, -2, -2, -50, -20],
        [100, -20, 10,  5,  5, 10, -20, 100]
    ]

    score = 0

    for i in range(8):
        for j in range(8):
            if board[i][j] == player:
                score += weights[i][j]
            elif board[i][j] == opponent:
                score -= weights[i][j]

    return score

def minimax(board, depth, player, maximizing_player, alpha, beta):
    valid_moves = get_valid_moves(board, player)
    if depth == 0 or not valid_moves:
        return evaluate_board(board, maximizing_player), None

    opponent = '●' if player == '○' else '○'

    if player == maximizing_player:
        max_eval = float('-inf')
        best_move = None
        for move in sorted(valid_moves, key=lambda m: evaluate_board(make_temp_move(board, m, player), player), reverse=True):
            temp_board = make_temp_move(board, move, player)
            eval, _ = minimax(temp_board, depth - 1, opponent, maximizing_player, alpha, beta)
            if eval > max_eval:
                max_eval = eval
                best_move = move
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval, best_move
    else:
        min_eval = float('inf')
        best_move = None
        for move in sorted(valid_moves, key=lambda m: evaluate_board(make_temp_move(board, m, opponent), opponent)):
            temp_board = make_temp_move(board, move, player)
            eval, _ = minimax(temp_board, depth - 1, opponent, maximizing_player, alpha, beta)
            if eval < min_eval:
                min_eval = eval
                best_move = move
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval, best_move

def make_temp_move(board, move, player):
    temp_board = [row[:] for row in board]
    make_move(temp_board, move[0], move[1], player)
    return temp_board

def ai_move(board, player):
    start_time = time.time()
    depth = 4
    best_move = None

    while time.time() - start_time < 10:  # 最大10秒の計算時間
        _, best_move_candidate = minimax(board, depth, player, player, float('-inf'), float('inf'))
        if best_move_candidate:
            best_move = best_move_candidate
        depth += 1

    return best_move

def count_stones(board):
    black_count = sum(row.count('●') for row in board)
    white_count = sum(row.count('○') for row in board)
    return black_count, white_count

def play_game():
    board = initialize_board()
    player_choice = input("先手(黒●)と後手(白○)のどちらを選びますか？(先手:1, 後手:2): ")
    if player_choice == "1":
        player = '●'
        ai = '○'
    else:
        player = '○'
        ai = '●'

    current_player = '●'

    while True:
        valid_moves = get_valid_moves(board, current_player)
        print_board(board)

        if not valid_moves:
            print(f"{current_player}に有効な手がありません。ターンをスキップします。")
            current_player = '○' if current_player == '●' else '●'
            valid_moves = get_valid_moves(board, current_player)

            if not valid_moves:
                print("両プレイヤーに有効な手がありません。ゲーム終了。")
                break
            continue

        if current_player == player:
            move = input("あなたの手を入力してください（例: d3）: ")
            if len(move) == 2 and move[0] in "abcdefgh" and move[1] in "12345678":
                col = ord(move[0]) - ord('a')
                row = int(move[1]) - 1

                if (row, col) in valid_moves:
                    make_move(board, row, col, current_player)
                    current_player = ai
                else:
                    print("無効な手です。もう一度入力してください。")
            else:
                print("入力形式が正しくありません。例: d3")
        else:
            print("AIが手を考えています...")
            move = ai_move(board, current_player)
            if move:
                make_move(board, move[0], move[1], current_player)
                move_notation = f"{chr(move[1] + ord('a'))}{move[0] + 1}"
                print(f"AIが置いた位置：{move_notation}")
                current_player = player

    black_count, white_count = count_stones(board)
    print_board(board)
    print(f"最終結果: 黒●={black_count}, 白○={white_count}")
    if black_count > white_count:
        print("黒●の勝利です！")
    elif white_count > black_count:
        print("白○の勝利です！")
    else:
        print("引き分けです！")

if __name__ == "__main__":
    play_game()
