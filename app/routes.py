from flask import current_app, jsonify, request, render_template, session, redirect, url_for
from .minesweeper.board_generation import generate_mines
from .minesweeper.board_reveal import check_victory, reveal_cells
from .minesweeper.solver import MinesweeperSolver
from .games import tic_tac_toe as ttt
from .games import snake as snake_game

@current_app.route('/')
def home():
    if not session.get('logged_in'):
        return render_template('login.html')

    if not session.get('logged_in'):
        return render_template('login.html')
    
    session['board'] = None
    session['first_move'] = True
    session['revealed_cells'] = []
    session['ttt_board'] = None
    session['ttt_current_player'] = 'X'
    session['snake_game'] = None
    
    return render_template('home.html')

@current_app.route('/minesweeper')
def minesweeper():
    session['board'] = None
    session['first_move'] = True
    if not session.get('logged_in'):
        return render_template('login.html')
    if not session.get('logged_in'):
        return render_template('login.html')
    
    session['board'] = None
    session['first_move'] = True
    session['revealed_cells'] = []
    
    return render_template('index.html', n=10, m=10)

@current_app.route('/snake')
def snake():
    if not session.get('logged_in'):
        return render_template('login.html')
    
    session['snake_game'] = None
    
    return render_template('snake.html')

@current_app.route('/tic-tac-toe')
def tic_tac_toe():
    if not session.get('logged_in'):
        return render_template('login.html')
    
    session['ttt_board'] = None
    session['ttt_current_player'] = 'X'
    
    return render_template('tic_tac_toe.html')

@current_app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('logged_in'):
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        users = session.get('users', {})
        if username in users and users[username] == password:
            session['logged_in'] = True
            session['username'] = username
            session['board'] = None
            session['first_move'] = True
            session['revealed_cells'] = []
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error='Invalid username or password')

    return render_template('login.html')

@current_app.route('/signup', methods=['GET', 'POST'])
def signup():
    if session.get('logged_in'):
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not username or len(username) < 3:
            return render_template('signup.html', error='Username must be at least 3 characters')
        
        if not password or len(password) < 6:
            return render_template('signup.html', error='Password must be at least 6 characters')
        
        if password != confirm_password:
            return render_template('signup.html', error='Passwords do not match')

        if 'users' not in session:
            session['users'] = {}
        
        users = session.get('users', {})
        if username in users:
            return render_template('signup.html', error='Username already exists')
        
        users[username] = password
        session['users'] = users
        
        session['logged_in'] = True
        session['username'] = username
        session['board'] = None
        session['first_move'] = True
        session['revealed_cells'] = []
        
        return redirect(url_for('home'))

    return render_template('signup.html')

@current_app.route('/logout')
def logout():
    users = session.get('users', {})
    session.clear()
    session['users'] = users
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

    if 'ttt_board' not in session or session['ttt_board'] is None:
        session['ttt_board'] = ttt.create_board()
        session['ttt_current_player'] = 'X'
    
    board = session['ttt_board']
    current_player = session['ttt_current_player']
    
    success, message = ttt.make_move(board, row, col, current_player)
    
    if not success:
        return jsonify({'success': False, 'message': message})
    
    winner = ttt.check_winner(board)
    
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
    
    if 'snake_game' not in session or session['snake_game'] is None:
        game = snake_game.create_game(rows=20, cols=20)
        session['snake_game'] = game
    else:
        game = session['snake_game']
    
    if direction:
        snake_game.change_direction(game, direction)
    
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
