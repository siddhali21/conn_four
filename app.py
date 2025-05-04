from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import math
import copy

app = Flask(__name__)
CORS(app)

ROWS = 6
COLS = 7
EMPTY = 0
PLAYER = 1
AI = 2

board = [[EMPTY for _ in range(COLS)] for _ in range(ROWS)]
game_over = False


def is_valid_location(board, col):
    return board[0][col] == EMPTY


def get_next_open_row(board, col):
    for r in reversed(range(ROWS)):
        if board[r][col] == EMPTY:
            return r
    return -1


def drop_piece(board, row, col, piece):
    board[row][col] = piece


def winning_move(board, piece):
    # Horizontal
    for c in range(COLS - 3):
        for r in range(ROWS):
            if all(board[r][c + i] == piece for i in range(4)):
                return True
    # Vertical
    for c in range(COLS):
        for r in range(ROWS - 3):
            if all(board[r + i][c] == piece for i in range(4)):
                return True
    # Positive diagonal
    for c in range(COLS - 3):
        for r in range(ROWS - 3):
            if all(board[r + i][c + i] == piece for i in range(4)):
                return True
    # Negative diagonal
    for c in range(COLS - 3):
        for r in range(3, ROWS):
            if all(board[r - i][c + i] == piece for i in range(4)):
                return True
    return False


def get_valid_locations(board):
    return [col for col in range(COLS) if is_valid_location(board, col)]


def minimax(board, depth, alpha, beta, maximizingPlayer):
    valid_locations = get_valid_locations(board)
    is_terminal = winning_move(board, PLAYER) or winning_move(board, AI) or len(valid_locations) == 0
    if depth == 0 or is_terminal:
        if winning_move(board, AI):
            return (None, 100000000000000)
        elif winning_move(board, PLAYER):
            return (None, -10000000000000)
        else:
            return (None, 0)

    if maximizingPlayer:
        value = -math.inf
        best_col = valid_locations[0]
        for col in valid_locations:
            temp_board = copy.deepcopy(board)
            row = get_next_open_row(temp_board, col)
            drop_piece(temp_board, row, col, AI)
            new_score = minimax(temp_board, depth - 1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                best_col = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return best_col, value
    else:
        value = math.inf
        best_col = valid_locations[0]
        for col in valid_locations:
            temp_board = copy.deepcopy(board)
            row = get_next_open_row(temp_board, col)
            drop_piece(temp_board, row, col, PLAYER)
            new_score = minimax(temp_board, depth - 1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                best_col = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return best_col, value


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/move', methods=['POST'])
def move():
    global board, game_over
    if game_over:
        return jsonify({'error': 'Game is over'}), 400

    data = request.get_json()
    col = data['column']
    if not is_valid_location(board, col):
        return jsonify({'error': 'Invalid move'}), 400

    row = get_next_open_row(board, col)
    drop_piece(board, row, col, PLAYER)
    if winning_move(board, PLAYER):
        game_over = True
        return jsonify({'board': board, 'winner': PLAYER})

    # AI move
    ai_col, _ = minimax(board, 4, -math.inf, math.inf, True)
    if ai_col is not None and is_valid_location(board, ai_col):
        ai_row = get_next_open_row(board, ai_col)
        drop_piece(board, ai_row, ai_col, AI)
        if winning_move(board, AI):
            game_over = True
            return jsonify({'board': board, 'winner': AI})

    return jsonify({'board': board})


@app.route('/reset', methods=['POST'])
def reset():
    global board, game_over
    board = [[EMPTY for _ in range(COLS)] for _ in range(ROWS)]
    game_over = False
    return jsonify({'message': 'Game reset'})


if __name__ == '__main__':
    app.run(debug=True)
