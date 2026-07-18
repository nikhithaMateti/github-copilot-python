from app import CURRENT


def test_index_route_returns_ok(client):
    response = client.get("/")
    assert response.status_code == 200


def test_index_route_contains_timer_display(client):
    response = client.get("/")
    assert response.status_code == 200

    body = response.get_data(as_text=True)
    assert 'id="timer"' in body
    assert '00:00' in body


def test_index_route_contains_scoreboard_elements(client):
    response = client.get("/")
    assert response.status_code == 200

    body = response.get_data(as_text=True)
    assert 'id="player-name"' in body
    assert 'id="scoreboard-list"' in body
    assert 'Top 10 Fastest Times' in body


def test_stylesheet_contains_subgrid_and_dark_mode_support(client):
    response = client.get('/static/styles.css')
    assert response.status_code == 200

    css = response.get_data(as_text=True)
    assert '.sudoku-cell.subgrid-a' in css
    assert '.sudoku-cell.subgrid-b' in css
    assert '@media (prefers-color-scheme: dark)' in css


def test_new_route_returns_puzzle(client):
    response = client.get("/new?clues=35")
    assert response.status_code == 200

    data = response.get_json()
    assert "puzzle" in data
    assert len(data["puzzle"]) == 9
    assert all(len(row) == 9 for row in data["puzzle"])


def test_check_route_without_active_game_returns_400(client):
    response = client.post("/check", json={"board": [[0] * 9 for _ in range(9)]})
    assert response.status_code == 400

    data = response.get_json()
    assert data.get("error") == "No game in progress"


def _count_prefilled_cells(board):
    return sum(1 for row in board for value in row if value != 0)


def test_new_route_honors_easy_difficulty(client):
    response = client.get("/new?difficulty=easy")
    assert response.status_code == 200

    data = response.get_json()
    assert "puzzle" in data
    assert _count_prefilled_cells(data["puzzle"]) == 45


def test_new_route_honors_medium_difficulty(client):
    response = client.get("/new?difficulty=medium")
    assert response.status_code == 200

    data = response.get_json()
    assert "puzzle" in data
    assert _count_prefilled_cells(data["puzzle"]) == 35


def test_new_route_honors_hard_difficulty(client):
    response = client.get("/new?difficulty=hard")
    assert response.status_code == 200

    data = response.get_json()
    assert "puzzle" in data
    assert _count_prefilled_cells(data["puzzle"]) == 28


def test_new_route_invalid_difficulty_falls_back_to_clues(client):
    response = client.get("/new?difficulty=unknown&clues=40")
    assert response.status_code == 200

    data = response.get_json()
    assert "puzzle" in data
    assert _count_prefilled_cells(data["puzzle"]) == 40


def test_hint_route_without_active_game_returns_400(client):
    response = client.post("/hint")
    assert response.status_code == 400

    data = response.get_json()
    assert data.get("error") == "No game in progress"


def test_hint_route_fills_exactly_one_empty_cell_with_correct_value(client):
    start_response = client.get("/new?difficulty=hard")
    assert start_response.status_code == 200

    start_puzzle = start_response.get_json()["puzzle"]
    start_filled = _count_prefilled_cells(start_puzzle)

    hint_response = client.post("/hint")
    assert hint_response.status_code == 200
    hint_data = hint_response.get_json()

    hint = hint_data.get("hint")
    assert hint is not None

    row = hint["row"]
    col = hint["col"]
    value = hint["value"]

    assert start_puzzle[row][col] == 0
    assert CURRENT["solution"][row][col] == value
    assert CURRENT["puzzle"][row][col] == value
    assert _count_prefilled_cells(CURRENT["puzzle"]) == start_filled + 1


def _find_two_empty_positions(board):
    empty_positions = []
    for row_index in range(9):
        for col_index in range(9):
            if board[row_index][col_index] == 0:
                empty_positions.append((row_index, col_index))
                if len(empty_positions) == 2:
                    return empty_positions
    return empty_positions


def _wrong_value(expected):
    return 1 if expected != 1 else 2


def test_check_route_returns_only_incorrect_filled_entries(client):
    start_response = client.get("/new?difficulty=hard")
    assert start_response.status_code == 200

    puzzle = start_response.get_json()["puzzle"]
    solution = CURRENT["solution"]
    positions = _find_two_empty_positions(puzzle)
    assert len(positions) == 2

    wrong_row, wrong_col = positions[0]
    correct_row, correct_col = positions[1]

    submitted = [row[:] for row in puzzle]
    submitted[wrong_row][wrong_col] = _wrong_value(solution[wrong_row][wrong_col])
    submitted[correct_row][correct_col] = solution[correct_row][correct_col]

    response = client.post("/check", json={"board": submitted})
    assert response.status_code == 200

    incorrect = response.get_json()["incorrect"]
    assert [wrong_row, wrong_col] in incorrect
    assert [correct_row, correct_col] not in incorrect
