import os

from flask import Flask

from GameListener import game_listener
from RequestsListener import base_request_listener
from TasksRequestsListener import tasks_request_listener

app = Flask(__name__)
app.secret_key = '4fh2784f4f2h9784h3g7980g91q3o47h8'

app.register_blueprint(base_request_listener, url_prefix='/')
app.register_blueprint(tasks_request_listener, url_prefix='/')
app.register_blueprint(game_listener, url_prefix='/')

if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(host='0.0.0.0', port=2565, debug=False)
