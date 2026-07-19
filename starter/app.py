from flask import Flask, render_template, jsonify, request
import sudoku_logic
import random

app = Flask(__name__)

# Keep a simple in-memory store for current puzzle and solution
CURRENT = {
    'puzzle': None,
    'solution': None
}

DIFFICULTY_CLUES = {
    'easy': 45,
    'medium': 35,
    'hard': 28,
}


def _missing_game_response():
    return jsonify({'error': 'No game in progress'}), 400


def _collect_incorrect_positions(submitted_board, expected_solution):
    incorrect_positions = []
    for row_index in range(sudoku_logic.SIZE):
        for col_index in range(sudoku_logic.SIZE):
            submitted_value = submitted_board[row_index][col_index]
            expected_value = expected_solution[row_index][col_index]
            if submitted_value != sudoku_logic.EMPTY and submitted_value != expected_value:
                incorrect_positions.append([row_index, col_index])
    return incorrect_positions


def _empty_positions(board):
    empty_cells = []
    for row_index in range(sudoku_logic.SIZE):
        for col_index in range(sudoku_logic.SIZE):
            if board[row_index][col_index] == sudoku_logic.EMPTY:
                empty_cells.append((row_index, col_index))
    return empty_cells

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/new')
def new_game():
    requested_difficulty = request.args.get('difficulty', '').strip().lower()
    if requested_difficulty in DIFFICULTY_CLUES:
        clues = DIFFICULTY_CLUES[requested_difficulty]
    else:
        clues = int(request.args.get('clues', 35))

    puzzle, solution = sudoku_logic.generate_puzzle(clues)
    CURRENT['puzzle'] = puzzle
    CURRENT['solution'] = solution
    return jsonify({'puzzle': puzzle})

@app.route('/check', methods=['POST'])
def check_solution():
    request_payload = request.json
    submitted_board = request_payload.get('board')
    current_solution = CURRENT.get('solution')

    if current_solution is None:
        return _missing_game_response()

    incorrect_positions = _collect_incorrect_positions(submitted_board, current_solution)
    return jsonify({'incorrect': incorrect_positions})


@app.route('/hint', methods=['POST'])
def reveal_hint():
    request_payload = request.json
    submitted_board = request_payload.get('board')

    current_solution = CURRENT.get('solution')

    if submitted_board is None or current_solution is None:
        return _missing_game_response()

    available_positions = _empty_positions(submitted_board)

    if not available_positions:
        return jsonify({'hint': None, 'message': 'No empty cells available'})

    row_index, col_index = random.choice(available_positions)
    hinted_value = current_solution[row_index][col_index]

    submitted_board[row_index][col_index] = hinted_value

    return jsonify({
        'hint': {
            'row': row_index,
            'col': col_index,
            'value': hinted_value,
        },
        'puzzle': submitted_board,
    })
if __name__ == '__main__':
    app.run(debug=True)