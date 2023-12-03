from flask_socketio import SocketIO

socketio = SocketIO()


@socketio.on('connect')
def handle_connect():
    print('подключение')


@socketio.on('message')
def handle_message(message):
    print(f'получено: {message}')