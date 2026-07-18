import copy
import random

SIZE = 9
EMPTY = 0
BOX_SIZE = 3

def deep_copy(board):
    return copy.deepcopy(board)

def create_empty_board():
    return [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]


def _number_in_row(board, row, number):
    for column_index in range(SIZE):
        if board[row][column_index] == number:
            return True
    return False


def _number_in_column(board, column, number):
    for row_index in range(SIZE):
        if board[row_index][column] == number:
            return True
    return False


def _number_in_box(board, row, col, number):
    box_start_row = row - row % BOX_SIZE
    box_start_col = col - col % BOX_SIZE
    for row_offset in range(BOX_SIZE):
        for col_offset in range(BOX_SIZE):
            if board[box_start_row + row_offset][box_start_col + col_offset] == number:
                return True
    return False


def _find_empty_cell(board):
    for row_index in range(SIZE):
        for col_index in range(SIZE):
            if board[row_index][col_index] == EMPTY:
                return row_index, col_index
    return None

def is_safe(board, row, col, num):
    if _number_in_row(board, row, num):
        return False
    if _number_in_column(board, col, num):
        return False
    if _number_in_box(board, row, col, num):
        return False
    return True

def fill_board(board):
    empty_cell = _find_empty_cell(board)
    if empty_cell is None:
        return True

    row, col = empty_cell
    candidate_numbers = list(range(1, SIZE + 1))
    random.shuffle(candidate_numbers)

    for candidate in candidate_numbers:
        if is_safe(board, row, col, candidate):
            board[row][col] = candidate
            if fill_board(board):
                return True
            board[row][col] = EMPTY

    return False


def _count_solutions(board, limit=2):
    if limit <= 0:
        return 0

    empty_cell = _find_empty_cell(board)
    if empty_cell is None:
        return 1

    row, col = empty_cell
    solutions_found = 0

    for candidate in range(1, SIZE + 1):
        if is_safe(board, row, col, candidate):
            board[row][col] = candidate
            solutions_found += _count_solutions(board, limit=limit - solutions_found)
            board[row][col] = EMPTY

            if solutions_found >= limit:
                break

    return solutions_found


def has_unique_solution(board):
    board_copy = deep_copy(board)
    return _count_solutions(board_copy, limit=2) == 1


def _remove_cells_while_preserving_uniqueness(board, clues):
    cells_to_remove = SIZE * SIZE - clues
    positions = [(row_index, col_index) for row_index in range(SIZE) for col_index in range(SIZE)]
    random.shuffle(positions)

    removed_cells = 0
    for row_index, col_index in positions:
        if removed_cells == cells_to_remove:
            break

        original_value = board[row_index][col_index]
        board[row_index][col_index] = EMPTY

        if _count_solutions(board, limit=2) == 1:
            removed_cells += 1
        else:
            board[row_index][col_index] = original_value

    return removed_cells == cells_to_remove

def remove_cells(board, clues):
    cells_to_remove = SIZE * SIZE - clues
    while cells_to_remove > 0:
        row_index = random.randrange(SIZE)
        col_index = random.randrange(SIZE)
        if board[row_index][col_index] != EMPTY:
            board[row_index][col_index] = EMPTY
            cells_to_remove -= 1

def generate_puzzle(clues=35):
    if clues < 0 or clues > SIZE * SIZE:
        raise ValueError(f'clues must be between 0 and {SIZE * SIZE}')

    max_attempts = 100
    for _ in range(max_attempts):
        generated_board = create_empty_board()
        fill_board(generated_board)
        solution = deep_copy(generated_board)
        puzzle = deep_copy(generated_board)

        if _remove_cells_while_preserving_uniqueness(puzzle, clues):
            return puzzle, solution

    raise RuntimeError('Unable to generate a uniquely solvable puzzle with requested clues')
