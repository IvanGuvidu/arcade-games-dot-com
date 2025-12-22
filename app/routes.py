from flask import current_app, jsonify, request, render_template, session
from .board.board_generation import generate_mines
from .board.board_reveal import reveal_cells

@current_app.route('/')
def home():
    return render_template('index.html', n = 10, m = 10)

@current_app.route('/restart', methods=['POST'])
def restart_game():
    session['board'] = None
    session['first_move'] = True
    return jsonify({"success": True})

@current_app.route('/reveal', methods=['POST'])
def reveal():
    data = request.get_json()
    row = data['row']
    col = data['col']
    
    if session.get('first_move', True):
        board = generate_mines(
            rows=10,
            cols=10,
            mines=15,
            first_row=row,
            first_col=col
        )
        session['board'] = board
        session['first_move'] = False
    else:
        board = session.get('board')
    
    cell_val = board[row][col]
    if cell_val == 'M':
        return jsonify({'mine': True, 'adjacentMines': 0, 'revealed': []})
    else:
        revealed = list(reveal_cells(board, row, col))
        return jsonify({'mine': False, 'adjacentMines': cell_val, 'revealed': revealed})
