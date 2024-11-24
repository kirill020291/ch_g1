from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room
import chess

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Состояние игр для каждой комнаты
games = {}

# Класс для управления шахматной игрой
class ChessEngine:
    def __init__(self):
        self.board = chess.Board()

    def make_move(self, move):
        try:
            uci_move = chess.Move.from_uci(move)
            if uci_move in self.board.legal_moves:
                self.board.push(uci_move)
                return True
            return False
        except ValueError:
            return False

    def get_board(self):
        return [[str(self.board.piece_at(chess.square(col, row)) or '--') for col in range(8)] for row in range(7, -1, -1)]

# Обработчик подключения к комнате
@socketio.on('join_game')
def join_game(data):
    room_id = data['roomId']
    join_room(room_id)
    if room_id not in games:
        games[room_id] = ChessEngine()
    if len(socketio.server.manager.rooms.get(room_id, [])) == 2:  # Проверяем, что два игрока в комнате
        emit('game_start', room=room_id)

# Обработчик хода игрока
@socketio.on('move')
def move(data):
    room_id = data['roomId']
    move = data['move']
    game = games[room_id]
    if game.make_move(move['from'] + move['to']):
        board = game.get_board()
        emit('update_board', {'board': board, 'move': move}, room=room_id)

# Маршрут для отображения HTML-страницы
@app.route('/')
def chess_view():
    return render_template('index.html')  # Укажите путь к вашему HTML-файлу

# Запуск сервера
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8000)
