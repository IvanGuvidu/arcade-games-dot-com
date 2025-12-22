import random

def generate_mines(rows = 10, cols = 10, mines = 15, first_row=None, first_col=None):
    mines_positions = set()
    forbidden = set()
    if first_row is not None and first_col is not None:
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                nr, nc = first_row + dx, first_col + dy
                if 0 <= nr < rows and 0 <= nc < cols:
                    forbidden.add((nr, nc))
    
    while len(mines_positions) < mines:
        r = random.randint(0, rows - 1)
        c = random.randint(0, cols - 1)
        if (r, c) in mines_positions or (r, c) in forbidden:
            continue
        forbidden.add((r, c))
        mines_positions.add((r, c))

    board = [[0 for _ in range(cols)] for _ in range(rows)]
    for r, c in mines_positions:
        board[r][c] = 'M'

    for r in range(rows):
        for c in range(cols):
            if board[r][c] != 'M':
                count = 0
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        if dx == 0 and dy == 0:
                            continue
                        nr, nc = r + dx, c + dy
                        if 0 <= nr < rows and 0 <= nc < cols:
                            if board[nr][nc] == 'M':
                                count += 1
                board[r][c] = count
    return board
