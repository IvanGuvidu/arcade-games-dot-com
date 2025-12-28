from flask import current_app, jsonify, request, render_template, session, redirect, url_for
from .minesweeper.board_generation import generate_mines
from .minesweeper.board_reveal import check_victory, reveal_cells
from .minesweeper.solver import MinesweeperSolver
from .board.board_generation import generate_mines
from .board.board_reveal import check_victory, reveal_cells, reveal_cell_hint
from .games import tic_tac_toe as ttt

@current_app.route('/')
def home():
    if not session.get('logged_in'):
        return render_template('login.html')
    # If not logged in, show login page
    if not session.get('logged_in'):
        return render_template('login.html')
    
    # Reset all game states when returning to home
    session['board'] = None
    session['first_move'] = True
    session['revealed_cells'] = []
    session['ttt_board'] = None
    session['ttt_current_player'] = 'X'
    
    # Show the game selection home page
    return render_template('home.html')

@current_app.route('/minesweeper')
def minesweeper():
    session['board'] = None
    session['first_move'] = True
    if not session.get('logged_in'):
        return render_template('login.html')
    if not session.get('logged_in'):
        return render_template('login.html')
    
    # Reset minesweeper game state when entering the game
    session['board'] = None
    session['first_move'] = True
    session['revealed_cells'] = []
    
    return render_template('index.html', n=10, m=10)

@current_app.route('/snake')
def snake():
    if not session.get('logged_in'):
        return render_template('login.html')
    return render_template('snake.html')

@current_app.route('/tic-tac-toe')
def tic_tac_toe():
    if not session.get('logged_in'):
        return render_template('login.html')
    
    # Reset tic-tac-toe game state when entering the game
    session['ttt_board'] = None
    session['ttt_current_player'] = 'X'
    
    return render_template('tic_tac_toe.html')

@current_app.route('/login', methods=['GET', 'POST'])
def login():
    # If already logged in, go to home
    if session.get('logged_in'):
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form.get('username')
        session['logged_in'] = True
        session['username'] = username or 'Player'

        # Minimal login: accept any credentials and mark session
        username = request.form.get('username')
        # password is received but not validated in this simple demo
        session['logged_in'] = True
        session['username'] = username or 'Player'

        # Reset game state on login
        session['board'] = None
        session['first_move'] = True
        session['revealed_cells'] = []

        return redirect(url_for('home'))

    # GET -> render login page
    return render_template('login.html')

@current_app.route('/logout')
def logout():
    # Clear session and return to login
    session.clear()
    return redirect(url_for('home'))

@current_app.route('/restart', methods=['POST'])
def restart_game():
    session['board'] = None
    session['first_move'] = True
    session['flagged_cells'] = []
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
        session['flagged_cells'] = []
        session['revealed_cells'] = []
    else:
        board = session.get('board')
    
    cell_val = board[row][col]
    if cell_val == 'M':
        return jsonify({'mine': True, 'adjacentMines': 0, 'revealed': [], 'victory': False})
    else:
        revealed = list(reveal_cells(board, row, col))
        revealed_json = [{'row': r, 'col': c, 'value': board[r][c]} for r, c in revealed]

        revealed_cells = set(session.get('revealed_cells', []))
        revealed_cells.update([(r, c) for r, c in revealed])
        session['revealed_cells'] = list(revealed_cells)

        victory = check_victory(board, revealed_cells)

        return jsonify({'mine': False, 'adjacentMines': cell_val, 'revealed': revealed_json, 'victory': victory})
@current_app.route('/flag', methods=['POST'])
def flag():
    data = request.get_json()
    x = data['row']
    y = data['col']
    
    flagged_cells = session.get('flagged_cells', [])
    cell_tuple = (x, y)
    
    if cell_tuple in flagged_cells:
        flagged_cells.remove(cell_tuple)
        action = 'removed'
    else:
        flagged_cells.append(cell_tuple)
        action = 'added'
    
    session['flagged_cells'] = flagged_cells
    
    return jsonify({
        'success': True,
        'action': action,
        'flagged': len(flagged_cells)
    })

@current_app.route('/hint_cell', methods=['POST'])
def hint_cell():
    board = session.get('board')
    revealed = set(tuple(cell) for cell in session.get('revealed_cells', []))
    flags = set(tuple(cell) for cell in session.get('flagged_cells', []))

    solver_board = []
    for i in range(len(board)):
        row = []
        for j in range(len(board[0])):
            if (i, j) in revealed:
                row.append(str(board[i][j]))
            elif (i, j) in flags:
                row.append('F')
            else:
                row.append('.')
        solver_board.append(row)

    solver = MinesweeperSolver(solver_board)
    best_move = solver.get_best_move()

    if best_move:
        x, y = best_move['x'], best_move['y']
        revealed_cells = session.get('revealed_cells', [])
        action = best_move['action']

        if action == 'click' and (x, y) not in revealed:
            revealed_cells.append((x, y))
            session['revealed_cells'] = revealed_cells
            
            if board[x][y] == 'M':
                return jsonify({'row': -1, 'col': -1, 'value': -1, 'victory': False, 'action': action})
            
            victory = check_victory(board, set(revealed_cells))
            
            return jsonify({'row': x, 'col': y, 'value': board[x][y], 'victory': victory, 'action': action})
        
        if action == 'flag':
            flagged_cells = session.get('flagged_cells', [])
            if (x, y) not in flagged_cells:
                flagged_cells.append((x, y))
                session['flagged_cells'] = flagged_cells
            return jsonify({'row': x, 'col': y, 'value': -1, 'victory': False, 'action': action})

        return jsonify({'row': -1, 'col': -1, 'value': -1, 'victory': False, 'action': 'none'})
    else:
        return jsonify({'row': -1, 'col': -1, 'value': -1, 'victory': False})

@current_app.route('/tic-tac-toe/move', methods=['POST'])
def tic_tac_toe_move():
    if not session.get('logged_in'):
        return jsonify({'error': 'Not logged in'}), 401
    
    data = request.get_json()
    row = data['row']
    col = data['col']
    
    if 'ttt_board' not in session:
    # Initialize board if not exists or is None
    if 'ttt_board' not in session or session['ttt_board'] is None:
        session['ttt_board'] = ttt.create_board()
        session['ttt_current_player'] = 'X'
    
    board = session['ttt_board']
    current_player = session['ttt_current_player']
    
    # Make move
    success, message = ttt.make_move(board, row, col, current_player)
    
    if not success:
        return jsonify({'success': False, 'message': message})
    
    # Check for winner
    winner = ttt.check_winner(board)
    
    # Update session
    session['ttt_board'] = board
    
    if winner:
        game_over = True
        next_player = current_player
    else:
        next_player = ttt.get_next_player(current_player)
        session['ttt_current_player'] = next_player
        game_over = False
    
    return jsonify({
        'success': True,
        'board': board,
        'winner': winner,
        'gameOver': game_over,
        'nextPlayer': next_player
    })

@current_app.route('/tic-tac-toe/restart', methods=['POST'])
def tic_tac_toe_restart():
    if not session.get('logged_in'):
        return jsonify({'error': 'Not logged in'}), 401
    
    session['ttt_board'] = ttt.create_board()
    session['ttt_current_player'] = 'X'
    
    return jsonify({'success': True, 'currentPlayer': 'X'})
