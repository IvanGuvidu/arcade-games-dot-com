"""
Tic Tac Toe game logic
"""

def create_board():
    """Create an empty 3x3 board"""
    return [['' for _ in range(3)] for _ in range(3)]

def make_move(board, row, col, player):
    if board[row][col] != '':
        return False, "Cell already occupied"
    
    board[row][col] = player
    return True, "Move successful"

def check_winner(board):
    # Check rows
    for row in board:
        if row[0] == row[1] == row[2] and row[0] != '':
            return row[0]
    
    for col in range(3):
        if board[0][col] == board[1][col] == board[2][col] and board[0][col] != '':
            return board[0][col]
    
    # Check diagonals
    if board[0][0] == board[1][1] == board[2][2] and board[0][0] != '':
        return board[0][0]
    
    if board[0][2] == board[1][1] == board[2][0] and board[0][2] != '':
        return board[0][2]
    
    # Check for draw
    if all(board[row][col] != '' for row in range(3) for col in range(3)):
        return 'draw'
    
    return None

def get_next_player(current_player):
    """Toggle between X and O"""
    return 'O' if current_player == 'X' else 'X'
