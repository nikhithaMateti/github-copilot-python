import sudoku_logic


def test_home_page_is_reachable(client):
    response = client.get("/")
    assert response.status_code == 200


def test_generate_puzzle_defaults_to_9x9():
    puzzle, solution = sudoku_logic.generate_puzzle()

    assert len(puzzle) == 9
    assert len(solution) == 9
    assert all(len(row) == 9 for row in puzzle)
    assert all(len(row) == 9 for row in solution)
