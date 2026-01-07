# Unsolvable Exception class
class Unsolvable(Exception):
    pass

def lights_out_actions(board: list[list[int]]):
    # Create a copy of the board
    board = [row[:] for row in board]

    r = len(board)
    c = len(board[0]) if r > 0 else 0
    zero_board = [[0]*c for _ in range(r)]
    directions = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]

    first_last_cases: list[tuple[list[int], list[int]]] = []
    for case in range(2**c):
        case_board = [row[:] for row in zero_board]
        case_reduced = case
        current_idx = 0
        first = [0]*c
        while case_reduced > 0:
            idx = case_reduced % 2
            case_reduced = case_reduced // 2
            if idx == 1:
                first[current_idx] = 1
                for dr, dc in directions:
                    ni, nj = 0 + dr, current_idx + dc
                    if 0 <= ni < r and 0 <= nj < c:
                        case_board[ni][nj] ^= 1
            current_idx += 1
        for i in range(1, r):
            for j in range(c):
                if case_board[i-1][j] == 1:
                    for dr, dc in directions:
                        ni, nj = i + dr, j + dc
                        if 0 <= ni < r and 0 <= nj < c:
                            case_board[ni][nj] ^= 1
        last = [case_board[r-1][j] for j in range(c)]
        first_last_cases.append((first, last))

    # Track the number of toggles for each cell
    actions = [row[:] for row in zero_board]

    for i in range(1, r):
        for j in range(c):
            if board[i-1][j] == 1:
                for dr, dc in directions:
                    ni, nj = i + dr, j + dc
                    if 0 <= ni < r and 0 <= nj < c:
                        board[ni][nj] ^= 1
                actions[i][j] += 1

    actual_last = [board[r-1][j] for j in range(c)]

    correct_cases = [first for first, last in first_last_cases if last == actual_last]

    if not correct_cases:
        raise Unsolvable()

    chosen_first = correct_cases[0]
    for j in range(c):
        if chosen_first[j] == 1:
            for dr, dc in directions:
                ni, nj = 0 + dr, j + dc
                if 0 <= ni < r and 0 <= nj < c:
                    board[ni][nj] ^= 1
            actions[0][j] += 1
    for i in range(1, r):
        for j in range(c):
            if board[i-1][j] == 1:
                for dr, dc in directions:
                    ni, nj = i + dr, j + dc
                    if 0 <= ni < r and 0 <= nj < c:
                        board[ni][nj] ^= 1
                actions[i][j] += 1

    for i in range(r):
        for j in range(c):
            actions[i][j] = actions[i][j] % 2

    return actions

def lights_out(board: list[list[int]], actions: list[list[int]]):
    # Create a copy of the board
    board = [row[:] for row in board]
    r = len(board)
    c = len(board[0]) if r > 0 else 0
    directions = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]
    for i in range(r):
        for j in range(c):
            if actions[i][j] % 2 == 1:
                for dr, dc in directions:
                    ni, nj = i + dr, j + dc
                    if 0 <= ni < r and 0 <= nj < c:
                        board[ni][nj] ^= 1
    return board

def print_board(board: list[list[int]]):
    for row in board:
        print(' '.join(str(cell) for cell in row))

def run(initial_board: list[list[int]]):
    print("="*30)
    print("--- Lights Out Solver ---")
    print("-"*30)
    print("Initial Board:")
    print("-"*30)
    print_board(initial_board)
    print("-"*30)
    try:
        actions = lights_out_actions(initial_board)
        print("Actions:")
        print("-"*30)
        print_board(actions)
        print("-"*30)
        print("Board after solving Lights Out:")
        print("-"*30)
        board = lights_out(initial_board, actions)
        print_board(board)
        r = len(board)
        c = len(board[0]) if r > 0 else 0
        assert all(board[i][j] == 0 for i in range(r) for j in range(c)), "The board is not solved."
    except Unsolvable:
        print("The given board configuration is unsolvable.")
    print("="*30)

if __name__ == "__main__":
    # 0 0 0 0 0
    # 0 1 0 0 0
    # 0 0 0 0 0
    # 0 0 0 0 0
    # 0 0 0 0 0
    run([
        [0, 1, 0, 0, 0],
        [1, 1, 1, 0, 0],
        [0, 1, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
    ])

    # 0 0 0 0 0
    # 0 1 0 0 0
    # 0 0 0 0 0
    # 0 0 0 1 0
    # 1 0 0 0 0
    run([
        [0, 1, 0, 0, 0],
        [1, 1, 1, 0, 0],
        [0, 1, 0, 1, 0],
        [1, 0, 1, 1, 1],
        [1, 1, 0, 1, 0],
    ])

    # Unsolvable case
    run([
        [1, 1, 0, 1, 0],
        [1, 1, 0, 0, 1],
        [0, 1, 0, 0, 0],
        [1, 0, 1, 1, 1],
        [1, 0, 1, 0, 1],
    ])

    # 0 0 0 0 0
    # 0 1 0 0 0
    # 0 0 1 0 0
    # 0 0 0 1 0
    # 1 0 0 0 0
    run([
        [0, 1, 0, 0, 0],
        [1, 1, 0, 0, 0],
        [0, 0, 1, 0, 0],
        [1, 0, 0, 1, 1],
        [1, 1, 0, 1, 0],
    ])

    # 0 0 0 0 0 0
    # 0 1 0 0 0 0
    # 0 0 1 0 0 0
    # 0 0 0 1 0 0
    # 1 0 0 0 0 0
    # 0 0 0 0 0 0
    run([
        [0, 1, 0, 0, 0, 0],
        [1, 1, 0, 0, 0, 0],
        [0, 0, 1, 0, 0, 0],
        [1, 0, 0, 1, 1, 0],
        [1, 1, 0, 1, 0, 0],
        [1, 0, 0, 0, 0, 0],
    ])

    # 0 0 0 0 0 1
    # 0 1 0 0 1 1
    # 0 0 1 1 0 1
    # 0 0 1 0 1 0
    # 1 1 0 0 0 1
    # 1 1 0 1 0 1
    run([
        [0, 1, 0, 0, 0, 0],
        [1, 1, 0, 0, 0, 0],
        [0, 0, 1, 0, 0, 0],
        [1, 0, 0, 1, 1, 1],
        [1, 1, 0, 1, 0, 0],
        [1, 1, 0, 1, 0, 0],
    ])
