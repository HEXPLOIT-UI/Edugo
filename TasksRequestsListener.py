import json
import os
import uuid
from PIL import Image
from flask import render_template, request, redirect, url_for, session, jsonify, Flask, Blueprint

import DataBaseManagement
import Utils

tasks_request_listener = Blueprint('tasks_request_listener', __name__)


@tasks_request_listener.route('/create_page', methods=['GET', 'POST'])
def create_page():
    if 'logged_in' in session:
        if not session['logged_in']:
            return redirect(url_for('request_listener.index'))
        elif bool(DataBaseManagement.get_value_of_user(session['username'], "role") == "участник"):
            return redirect(url_for('request_listener.index'))
    else:
        return redirect(url_for('request_listener.index'))
    if request.method == 'POST':
        game_name = request.form['page_title']
        code = Utils.generate_random_string(6)
        owner = session['username']
        complete = False
        data = DataBaseManagement.load_data()
        data['GamesList'][code] = {
            'name': game_name,
            'complete': complete,
            'owner': owner,
            'leaderboard': {},
            'tasks': {}
        }
        DataBaseManagement.save_data(data)
        return redirect(url_for('tasks_request_listener.create_page_task', code=code, task_number=1))
    return render_template('create_page.html')


@tasks_request_listener.route('/create_page/<string:code>/task-<int:task_number>', methods=['GET', 'POST'])
def create_page_task(code, task_number):
    if 'logged_in' in session:
        if not session['logged_in']:
            return redirect(url_for('request_listener.index'))
        elif bool(DataBaseManagement.get_value_of_user(session['username'],"role") == "участник"):
            return redirect(url_for('request_listener.index'))
    else:
        return redirect(url_for('request_listener.index'))
    data = DataBaseManagement.load_data()
    if code not in data['GamesList']:
        return 'Игра не найдена', 404
    game_name = data['GamesList'][code]['name']
    if request.method == 'GET':
        return render_template('create_page_task.html'
                               , code=code, task_number=task_number, game_name=game_name)
    else:
        if 'task_type_test' in request.form:
            return redirect(url_for('tasks_request_listener.create_task_type', code=code, task_number=task_number, task_type="task_type_test"))
        elif 'task_type_quizz' in request.form:
            return redirect(url_for('tasks_request_listener.create_task_type', code=code, task_number=task_number, task_type="task_type_quizz"))
        elif 'task_type_checkboxs' in request.form:
            return redirect(url_for('tasks_request_listener.create_task_type', code=code, task_number=task_number, task_type="task_type_checkboxs"))
        elif 'create_game_button' in request.form:
            return redirect(url_for('tasks_request_listener.create_page_complete', code=code))
        else:
            return 'exploit', 403


@tasks_request_listener.route('/create_page/<string:code>/task-<int:task_number>/type-<string:task_type>', methods=['GET', 'POST'])
def create_task_type(code, task_number, task_type):
    if 'logged_in' in session:
        if not session['logged_in']:
            return redirect(url_for('request_listener.index'))
        elif bool(DataBaseManagement.get_value_of_user(session['username'],"role") == "участник"):
            return redirect(url_for('request_listener.index'))
    else:
        return redirect(url_for('request_listener.index'))
    data = DataBaseManagement.load_data()
    game_name = data['GamesList'][code]['name']
    if code not in data['GamesList']:
        return 'Игра не найдена', 404
    if request.method == 'GET':
        if task_type == 'task_type_test':
            return render_template('create_page_task.html'
                                   , code=code, task_number=task_number, game_name=game_name, task_type=task_type)
        elif task_type == 'task_type_quizz':
            return render_template('create_page_task.html'
                                   , code=code, task_number=task_number, game_name=game_name, task_type=task_type)
        elif task_type == 'task_type_checkboxs':
            return render_template('create_page_task.html'
                                   , code=code, task_number=task_number, game_name=game_name, task_type=task_type)
        else:
            return f'exploit {task_type}', 403
    else:
        if 'save-task-button-quizz' in request.form:
            example_field = request.form['example_field']
            try:
                correct_answer = int(request.form['save-task-button-quizz'])
            except:
                return 'Укажите правильный ответ'
            score_field = int(request.form['score_field'])
            i = 1
            if f'task-{task_number}' not in data['GamesList'][code]['tasks']:
                data['GamesList'][code]['tasks'][f'task-{task_number}'] = {}
                data['GamesList'][code]['tasks'][f'task-{task_number}']['answers'] = {}
            data['GamesList'][code]['tasks'][f'task-{task_number}']['name'] = example_field
            data['GamesList'][code]['tasks'][f'task-{task_number}']['type'] = "quizz"
            data['GamesList'][code]['tasks'][f'task-{task_number}']['score'] = score_field
            for value, key in request.form.items():
                if value.__contains__('quizButton'):
                    if f'answer-{i}' not in data['GamesList'][code]['tasks'][f'task-{task_number}']['answers']:
                        data['GamesList'][code]['tasks'][f'task-{task_number}']['answers'][f'answer-{i}'] = {}
                    correct = i == correct_answer
                    data['GamesList'][code]['tasks'][f'task-{task_number}']['answers'][f'answer-{i}']['name'] = key
                    data['GamesList'][code]['tasks'][f'task-{task_number}']['answers'][f'answer-{i}']['correct'] = correct
                    i = i + 1
            DataBaseManagement.save_data(data)
        if 'save-task-button-test' in request.form:
            example_field = request.form['example_field']
            answer_field = request.form['answer_field']
            score_field = request.form['score_field']
            if f'task-{task_number}' not in data['GamesList'][code]['tasks']:
                data['GamesList'][code]['tasks'][f'task-{task_number}'] = {}
            data['GamesList'][code]['tasks'][f'task-{task_number}']['name'] = example_field
            data['GamesList'][code]['tasks'][f'task-{task_number}']['type'] = "tests"
            data['GamesList'][code]['tasks'][f'task-{task_number}']['score'] = score_field
            data['GamesList'][code]['tasks'][f'task-{task_number}']['answer'] = answer_field
            DataBaseManagement.save_data(data)
        if 'save-task-button-checkboxs' in request.form:
            example_field = request.form['example_field']
            score_field = request.form['score_field']
            try:
                checkbox_data = json.loads(request.form['save-task-button-checkboxs'])
            except:
                return 'перед отправкой сохраните данные'
            if f'task-{task_number}' not in data['GamesList'][code]['tasks']:
                data['GamesList'][code]['tasks'][f'task-{task_number}'] = {}
                data['GamesList'][code]['tasks'][f'task-{task_number}']['answers'] = {}
            data['GamesList'][code]['tasks'][f'task-{task_number}']['name'] = example_field
            data['GamesList'][code]['tasks'][f'task-{task_number}']['type'] = "checkboxs"
            data['GamesList'][code]['tasks'][f'task-{task_number}']['score'] = score_field
            for item in checkbox_data:
                id = item['id']
                correct = item['checked']
                name = item['label']
                if f'answer-{id}' not in data['GamesList'][code]['tasks'][f'task-{task_number}']['answers']:
                    data['GamesList'][code]['tasks'][f'task-{task_number}']['answers'][f'answer-{id}'] = {}
                data['GamesList'][code]['tasks'][f'task-{task_number}']['answers'][f'answer-{id}']['correct'] = correct
                data['GamesList'][code]['tasks'][f'task-{task_number}']['answers'][f'answer-{id}']['name'] = name
            DataBaseManagement.save_data(data)
        if 'file' in request.files:
            file = request.files['file']
            if file.filename != '':
                filename = str(uuid.uuid4()) + '.' + file.filename.rsplit('.', 1)[1].lower()
                file_path = os.path.join("uploads", filename)
                file.save(file_path)
                image = Image.open(file_path)
                image_type = Utils.get_image_dimensions(image)
                if image_type == 'portrait':
                    target_width, target_height = 512, 768
                elif image_type == 'landscape':
                    target_width, target_height = 768, 512
                else:
                    target_width, target_height = 512, 512
                resized_image = Utils.resize_image(image, target_width, target_height)
                resized_image.save(file_path)
                data['GamesList'][code]['tasks'][f'task-{task_number}']['image'] = filename
                DataBaseManagement.save_data(data)
        return redirect(url_for('tasks_request_listener.create_page_task', code=code, task_number=task_number+1))


@tasks_request_listener.route('/create_page/<string:code>/complete', methods=['GET', 'POST'])
def create_page_complete(code):
    if 'logged_in' in session:
        if not session['logged_in']:
            return redirect(url_for('request_listener.index'))
        elif bool(DataBaseManagement.get_value_of_user(session['username'],"role") == "участник"):
            return redirect(url_for('request_listener.index'))
    else:
        return redirect(url_for('request_listener.index'))
    data = DataBaseManagement.load_data()
    if code not in data['GamesList']:
        return 'Игра не найдена', 404
    if data['GamesList'][code]['complete']:
        return 'Игра уже создана', 405
    if len(data['GamesList'][code]['tasks'].items()) <= 0:
        return 'Игра не доделана до конца', 405
    data['GamesList'][code]['complete'] = True
    DataBaseManagement.save_data(data)
    return render_template('game_created_page.html', code=code)


@tasks_request_listener.route('/my_games', methods=['GET', 'POST'])
def my_games():
    if 'logged_in' in session:
        if not session['logged_in']:
            return redirect(url_for('request_listener.index'))
        elif bool(DataBaseManagement.get_value_of_user(session['username'],"role") == "участник"):
            return redirect(url_for('request_listener.index'))
    else:
        return redirect(url_for('request_listener.index'))
    my_games_list = []
    data = DataBaseManagement.load_data()
    for code, user_data in data['GamesList'].items():
        if 'owner' in user_data and user_data['owner'] == session['username']:
            my_games_list.append({"code": code, "name": user_data['name']})
    if len(my_games_list) > 0:
        return render_template('my_games_page.html', my_games_list=my_games_list)
    else:
        return render_template('my_games_page.html', error="У вас нет игр")