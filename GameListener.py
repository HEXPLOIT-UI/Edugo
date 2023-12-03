import time

from flask import render_template, request, redirect, url_for, session, Blueprint

import DataBaseManagement
import Utils

game_listener = Blueprint('game_listener', __name__)

leaderboard_data = [
    {},
]


@game_listener.route('/play/<string:code>', methods=['GET', 'POST'])
def play(code):
    if 'logged_in' in session:
        if not session['logged_in']:
            return redirect(url_for('request_listener.index'))
    else:
        return redirect(url_for('request_listener.index'))
    data = DataBaseManagement.load_data()
    if code not in data['GamesList']:
        return render_template('error.html', error="Игра не найдена", redirect="/")
    if not data['GamesList'][code]['complete']:
        return render_template('error.html', error="Этот тест в процессе создания", redirect="/")
    permission = bool(DataBaseManagement.get_value_of_user(session['username'], "role") != "участник")
    if request.method == 'GET':
        return render_template('game_start_page.html', game_title=data['GamesList'][code]['name'], permission=permission)
    else:
        if 'playb' in request.form:
            return redirect(url_for(f'game_listener.solve_task', code=code, task_number=1))
        if 'checkb' in request.form:
            return redirect(url_for(f'game_listener.leaderboard', code=code))


@game_listener.route('/play/<string:code>/task-<int:task_number>', methods=['GET', 'POST'])
def solve_task(code, task_number):
    if 'logged_in' in session:
        if not session['logged_in']:
            return redirect(url_for('request_listener.index'))
    else:
        return redirect(url_for('request_listener.index'))
    data = DataBaseManagement.load_data()
    if code not in data['GamesList']:
        return render_template('error.html', error="Игра не найдена", redirect="/")
    permission = bool(DataBaseManagement.get_value_of_user(session['username'], "role") != "участник")
    if not data['GamesList'][code]['complete']:
        return render_template('game_start_page.html', game_title=data['GamesList'][code]['name'], permission=permission)
    login = session['username']
    if request.method == 'GET':
        if f'task-{task_number}' in data['GamesList'][code]['tasks']:
            if login in data['GamesList'][code]['leaderboard']:
                if f'task-{task_number}' in data['GamesList'][code]['leaderboard'][login]['tasks']:
                    lenght = len(data['GamesList'][code]['tasks'].items())
                    if task_number < lenght:
                        return redirect(url_for(f'game_listener.solve_task', code=code, task_number=task_number+1))
                    else:
                        return redirect(url_for(f'game_listener.end_game', code=code))
            task_type = data['GamesList'][code]['tasks'][f'task-{task_number}']['type']
            score = data['GamesList'][code]['tasks'][f'task-{task_number}']['score']
            question = data['GamesList'][code]['tasks'][f'task-{task_number}']['name']
            image = None
            if 'image' in data['GamesList'][code]['tasks'][f'task-{task_number}']:
                image = data['GamesList'][code]['tasks'][f'task-{task_number}']['image']
            if task_type == "tests":
                return render_template('game_page.html', task_number=task_number,
                                       game_title=data['GamesList'][code]['name'], question=question, score=score,
                                       task_type=task_type, image_link=image)
            if task_type == "quizz":
                answers = []
                for answer_id, answer_data in data['GamesList'][code]['tasks'][f'task-{task_number}'][
                    'answers'].items():
                    answers.append({'name': answer_data['name'], 'id': answer_id})
                return render_template('game_page.html', task_number=task_number,
                                       game_title=data['GamesList'][code]['name'], question=question, score=score,
                                       answers=answers, task_type=task_type, image_link=image)
            if task_type == "checkboxs":
                answers = []
                for answer_id, answer_data in data['GamesList'][code]['tasks'][f'task-{task_number}'][
                    'answers'].items():
                    answers.append({'name': answer_data['name'], 'id': answer_id})
                return render_template('game_page.html', task_number=task_number,
                                       game_title=data['GamesList'][code]['name'], question=question, score=score,
                                       answers=answers, task_type=task_type, image_link=image)
        else:
            return render_template('error.html', error=f"Задание {task_number} не найдено в этом тесте", redirect=f"/play/{code}")
    else:
        if 'sendanswerb' in request.form:
            if login in data['GamesList'][code]['leaderboard']:
                if f'task-{task_number}' in data['GamesList'][code]['leaderboard'][login]['tasks']:
                    return "exploit"
            task_type = data['GamesList'][code]['tasks'][f'task-{task_number}']['type']
            login = session['username']
            lenght = len(data['GamesList'][code]['tasks'].items())
            if login not in data['GamesList'][code]['leaderboard']:
                data['GamesList'][code]['leaderboard'][login] = {}
                data['GamesList'][code]['leaderboard'][login]['complete'] = False
                data['GamesList'][code]['leaderboard'][login]['score'] = 0
                data['GamesList'][code]['leaderboard'][login]['tasks'] = {}
                data['GamesList'][code]['leaderboard'][login]['start-time'] = int(time.time() * 1000)
                data['GamesList'][code]['leaderboard'][login]['end-time'] = 0
            if task_type == "tests":
                answer = bool(
                    data['GamesList'][code]['tasks'][f'task-{task_number}']['answer'] == request.form['answer_field'])
                if f'task-{task_number}' not in data['GamesList'][code]['leaderboard'][login]["tasks"]:
                    if bool(answer):
                        data['GamesList'][code]['leaderboard'][login]['score'] = (int(data['GamesList'][code]['leaderboard'][login]['score']) + int(data['GamesList'][code]['tasks'][f'task-{task_number}']['score']))
                    data['GamesList'][code]['leaderboard'][login]["tasks"][f'task-{task_number}'] = {}
                    data['GamesList'][code]['leaderboard'][login]["tasks"][f'task-{task_number}']['cache'] = bool(answer)
                    data['GamesList'][code]['leaderboard'][login]["tasks"][f'task-{task_number}']['answer'] = request.form['answer_field']
                    DataBaseManagement.save_data(data)
            if task_type == "quizz":
                user_answer = request.form['sendanswerb']
                try:
                    if f'task-{task_number}' not in data['GamesList'][code]['leaderboard'][login]["tasks"]:
                        if data['GamesList'][code]['tasks'][f'task-{task_number}']['answers'][user_answer]['correct']:
                            data['GamesList'][code]['leaderboard'][login]['score'] = (int(data['GamesList'][code]['leaderboard'][login]['score']) + int(data['GamesList'][code]['tasks'][f'task-{task_number}']['score']))
                        data['GamesList'][code]['leaderboard'][login]["tasks"][f'task-{task_number}'] = {}
                        data['GamesList'][code]['leaderboard'][login]["tasks"][f'task-{task_number}']['cache'] = bool(data['GamesList'][code]['tasks'][f'task-{task_number}']['answers'][user_answer]['correct'])
                        data['GamesList'][code]['leaderboard'][login]["tasks"][f'task-{task_number}']['answer'] = str(user_answer)
                        DataBaseManagement.save_data(data)
                except:
                    error = "Укажите правильный ответ"
                    return error
            if task_type == 'checkboxs':
                user_answers = request.form['sendanswerb']
                if user_answers == "None":
                    return "Укажите ответ"
                answer_list = user_answers.split(',')
                k = 0
                j = 0
                correct = False
                for answer_id, answer_data in data['GamesList'][code]['tasks'][f'task-{task_number}']['answers'].items():
                    if answer_data['correct']:
                        k = k + 1
                        if answer_id in answer_list:
                            j = j + 1
                if k == j:
                    correct = True
                if f'task-{task_number}' not in data['GamesList'][code]['leaderboard'][login]["tasks"]:
                    if correct:
                        data['GamesList'][code]['leaderboard'][login]['score'] = (int(data['GamesList'][code]['leaderboard'][login]['score']) + int(data['GamesList'][code]['tasks'][f'task-{task_number}']['score']))
                    data['GamesList'][code]['leaderboard'][login]["tasks"][f'task-{task_number}'] = {}
                    data['GamesList'][code]['leaderboard'][login]["tasks"][f'task-{task_number}']['cache'] = correct
                    data['GamesList'][code]['leaderboard'][login]["tasks"][f'task-{task_number}']['answer'] = str(user_answers)
                DataBaseManagement.save_data(data)
            if task_number >= lenght:
                data['GamesList'][code]['leaderboard'][login]['complete'] = True
                data['GamesList'][code]['leaderboard'][login]['end-time'] = int(time.time() * 1000)
                DataBaseManagement.save_data(data)
                return redirect(url_for(f'game_listener.end_game', code=code))
            return redirect(url_for(f'game_listener.solve_task', code=code, task_number=task_number + 1))
        else:
            return 'bad request'


@game_listener.route('/play/<string:code>/end', methods=['GET', 'POST'])
def end_game(code):
    if 'logged_in' in session:
        if not session['logged_in']:
            return redirect(url_for('request_listener.index'))
    else:
        return redirect(url_for('request_listener.index'))
    data = DataBaseManagement.load_data()
    if code not in data['GamesList']:
        return 'Игра не найдена', 404
    if not data['GamesList'][code]['complete']:
        return 'Эта игра еще не завершена {tasks for this game is not found}', 404
    if request.method == 'GET':
        if session['username'] not in data['GamesList'][code]['leaderboard']:
            return 'не удалось загрузить результат'
        result = Utils.get_result_of_game(code, session['username'])
        return render_template('game_end_page.html', game_title=data['GamesList'][code]['name'],
                               results=result)
    else:
        if 'leaderboardb' in request.form:
            return redirect(url_for(f'game_listener.leaderboard', code=code))


@game_listener.route('/play/<string:code>/leaderboard', methods=['GET', 'POST'])
def leaderboard(code):
    if 'logged_in' in session:
        if not session['logged_in']:
            return redirect(url_for('request_listener.index'))
    else:
        return redirect(url_for('request_listener.index'))
    data = DataBaseManagement.load_data()
    if code not in data['GamesList']:
        return render_template('error.html', error="Игра не найдена")
    if not data['GamesList'][code]['complete']:
        return 'Эта игра еще не завершена {tasks for this game is not found}', 404
    Utils.collect_stats_and_sort(code)
    game_name = data['GamesList'][code]['name']
    permission = bool(DataBaseManagement.get_value_of_user(session['username'], "role") != "участник")
    return render_template('game_leaderboard_page.html', code=code, leaderboard=leaderboard_data, game_name=game_name, permission=permission)


@game_listener.route('/play/<string:code>/check/<string:login>', methods=['GET', 'POST'])
def check(code, login):
    if 'logged_in' in session:
        if not session['logged_in']:
            return redirect(url_for('request_listener.index'))
    else:
        return redirect(url_for('request_listener.index'))
    data = DataBaseManagement.load_data()
    if code not in data['GamesList']:
        return 'Игра не найдена', 404
    if not data['GamesList'][code]['complete']:
        return 'Эта игра еще не завершена {tasks for this game is not found}', 404
    if request.method == 'GET':
        if login not in data['GamesList'][code]['leaderboard']:
            return 'не удалось загрузить результат'
        result = Utils.get_result_of_game(code, login)
        return render_template('game_end_page.html', game_title=data['GamesList'][code]['name'],
                               results=result)
    else:
        if 'leaderboardb' in request.form:
            return redirect(url_for(f'game_listener.leaderboard', code=code))