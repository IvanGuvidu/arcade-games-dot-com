from flask import current_app, jsonify, request, render_template, session, redirect, url_for
from .minesweeper.board_generation import generate_mines
from .minesweeper.board_reveal import check_victory, reveal_cells
from .minesweeper.solver import MinesweeperSolver
from .board.board_generation import generate_mines
from .board.board_reveal import check_victory, reveal_cells, reveal_cell_hint
from .games import tic_tac_toe as ttt
from .games import snake as snake_game

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
    session['snake_game'] = None
    
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
    
    # Reset snake game state when entering the game
    session['snake_game'] = None
    
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
    if session.get('logged_in'):
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form.get('username')
        session['logged_in'] = True
        session['username'] = username or 'Player'

        # Minimal login: accept any credentials and mark session
        username = request.form.get('username')
        session['logged_in'] = True
        session['username'] = username or 'Player'

        session['board'] = None
        session['first_move'] = True
        session['revealed_cells'] = []

        return redirect(url_for('home'))

    return render_template('login.html')

@current_app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@current_app.route('/restart', methods=['POST'])
def restart_game():
    session['board'] = None
    session['first_move'] = True
    session['flagged_cells'] = []
    return jsonify({"success": True})

@current_app.route('/hint_cell', methods=['POST'])
def hint_cell():
    if not session.get('logged_in'):
        return jsonify({'error': 'Not logged in'}), 401
    
    board = session.get('board')
    if not board:
        return jsonify({'row': -1, 'col': -1, 'value': -1, 'victory': False})
    
    revealed_cells = set(session.get('revealed_cells', []))
    hint_result = reveal_cell_hint(board, revealed_cells)
    
    if hint_result:
        row, col = hint_result
        cell_value = board[row][col]
        
        # Add to revealed cells
        revealed_cells.add((row, col))
        session['revealed_cells'] = list(revealed_cells)
        
        # Check for victory
        victory = check_victory(board, revealed_cells)
        
        return jsonify({'row': row, 'col': col, 'value': cell_value, 'victory': victory})
    else:
        return jsonify({'row': -1, 'col': -1, 'value': -1, 'victory': False})

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

@current_app.route('/tic-tac-toe/move', methods=['POST'])
def tic_tac_toe_move():
    if not session.get('logged_in'):
        return jsonify({'error': 'Not logged in'}), 401
    
    data = request.get_json()
    row = data['row']
    col = data['col']
    
<<<<<<< HEAD
    if 'ttt_board' not in session:
=======
<<<<<<< HEAD
>>>>>>> ca5380d (ce fac aici)
    # Initialize board if not exists or is None
    if 'ttt_board' not in session or session['ttt_board'] is None:
=======
    if 'ttt_board' not in session:
>>>>>>> dd357ef (remove comm)
        session['ttt_board'] = ttt.create_board()
        session['ttt_current_player'] = 'X'
    
    board = session['ttt_board']
    current_player = session['ttt_current_player']
    
    success, message = ttt.make_move(board, row, col, current_player)
    
    if not success:
        return jsonify({'success': False, 'message': message})
    
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

@current_app.route('/snake/init', methods=['POST'])
def snake_init():
    if not session.get('logged_in'):
        return jsonify({'error': 'Not logged in'}), 401
    
    game = snake_game.create_game(rows=20, cols=20)
    session['snake_game'] = game
    
    return jsonify(snake_game.get_game_state(game))

@current_app.route('/snake/move', methods=['POST'])
def snake_move():
    if not session.get('logged_in'):
        return jsonify({'error': 'Not logged in'}), 401
    
    data = request.get_json()
    direction = data.get('direction')
    
    # Initialize game if not exists
    if 'snake_game' not in session or session['snake_game'] is None:
        game = snake_game.create_game(rows=20, cols=20)
        session['snake_game'] = game
    else:
        game = session['snake_game']
    
    # Change direction if provided
    if direction:
        snake_game.change_direction(game, direction)
    
    # Move snake
    game = snake_game.move_snake(game)
    session['snake_game'] = game
    
    return jsonify(snake_game.get_game_state(game))

@current_app.route('/snake/restart', methods=['POST'])
def snake_restart():
    if not session.get('logged_in'):
        return jsonify({'error': 'Not logged in'}), 401
    
    game = snake_game.create_game(rows=20, cols=20)
    session['snake_game'] = game
    
    return jsonify(snake_game.get_game_state(game))
