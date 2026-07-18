import sudoku_logic
import pytest


def test_create_empty_board_has_expected_shape_and_values():
    board = sudoku_logic.create_empty_board()
    assert len(board) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in board)
    assert all(cell == sudoku_logic.EMPTY for row in board for cell in row)


def test_generate_puzzle_returns_two_9x9_boards():
    puzzle, solution = sudoku_logic.generate_puzzle(clues=35)

    assert len(puzzle) == sudoku_logic.SIZE
    assert len(solution) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in puzzle)
    assert all(len(row) == sudoku_logic.SIZE for row in solution)


def test_generate_puzzle_has_requested_clue_count():
    clues = 35
    puzzle, _ = sudoku_logic.generate_puzzle(clues=clues)
    non_empty = sum(1 for row in puzzle for value in row if value != sudoku_logic.EMPTY)
    assert non_empty == clues


@pytest.mark.parametrize('clues', [45, 35, 28])
def test_generate_puzzle_has_unique_solution(clues):
    puzzle, _ = sudoku_logic.generate_puzzle(clues=clues)
    assert sudoku_logic.has_unique_solution(puzzle)
