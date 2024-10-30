from flask import Flask, render_template, request, session, redirect, url_for
from game_state import CheckersGame

app = Flask(__name__)
app.secret_key = 'your-secret-key'


@app.route('/')
def index():
    return render_template('checkers_index.html')


@app.route('/new_game', methods=['POST'])
def new_game():
    # Initialize new game and store in session
    game = CheckersGame()
    session['game_state'] = game.serialize()
    return redirect(url_for('play'))


@app.route('/play')
def play():
    if 'game_state' not in session:
        return redirect(url_for('index'))

    game = CheckersGame.deserialize(session['game_state'])
    return render_template(
        'checkers_play.html',
        board=game.board,
        current_player=game.current_player,
        selected_piece=game.selected_piece,
        valid_moves=game.valid_moves,
        must_capture=game.must_capture,
        game_over=game.is_game_over(),
        winner=game.winner
    )


@app.route('/select', methods=['POST'])
def select_piece():
    row = int(request.form['row'])
    col = int(request.form['col'])

    game = CheckersGame.deserialize(session['game_state'])
    game.select_piece(row, col)
    session['game_state'] = game.serialize()

    return redirect(url_for('play'))


@app.route('/move', methods=['POST'])
def move_piece():
    row = int(request.form['row'])
    col = int(request.form['col'])

    game = CheckersGame.deserialize(session['game_state'])
    game.make_move(row, col)
    session['game_state'] = game.serialize()

    return redirect(url_for('play'))


if __name__ == '__main__':
    app.run(debug=True)