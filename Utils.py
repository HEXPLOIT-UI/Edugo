import string
import random
from PIL import Image
import DataBaseManagement
import GameListener


def generate_random_string(length):
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string


def get_game_complete_time(code, login):
    data = DataBaseManagement.load_data()
    time_in_ms = int(data['GamesList'][code]['leaderboard'][login]['end-time']) - int(
        data['GamesList'][code]['leaderboard'][login]['start-time'])
    seconds, milliseconds = divmod(time_in_ms, 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def get_result_of_game(code, login):
    data = DataBaseManagement.load_data()
    result = []
    """
    for task_id, task_data in data['GamesList'][code]['leaderboard'][login]['tasks']:
        task_type = data['GamesList'][code]['tasks'][task_id]['type']
    """
    for task_id, task_data in data['GamesList'][code]['tasks'].items():
        task_type = task_data['type']
        image = None
        if 'image' in task_data:
            image = task_data['image']
        if task_id not in data['GamesList'][code]['leaderboard'][login]['tasks']:
            correct_answer = None
            if task_type == 'tests':
                correct_answer = task_data['answer']
            elif task_type == 'quizz':
                correct_answer = None
                for answer, answer_data in data['GamesList'][code]['tasks'][task_id]['answers'].items():
                    if answer_data['correct']:
                        correct_answer = answer
                correct_answer_text = data['GamesList'][code]['tasks'][task_id]['answers'][correct_answer]['name']
                correct_answer = correct_answer_text
            elif task_type == 'checkboxs':
                correct_answers = []
                for answer_id, answer_data in data['GamesList'][code]['tasks'][task_id]['answers'].items():
                    if answer_data['correct']:
                        correct_answers.append(answer_data['name'])
                correct_answer = correct_answers
            result.append({'task_type': task_type, 'name': task_data['name'], 'user_answer': "None",
                           'correct_answer': correct_answer, 'correct': False, 'image': image})
        else:
            user_answer = data['GamesList'][code]['leaderboard'][login]['tasks'][task_id]['answer']
            if task_type == 'tests':
                correct_answer = task_data['answer']
                correct = bool(user_answer.lower() == correct_answer.lower())
                result.append({'task_type': task_type, 'name': task_data['name'], 'user_answer': user_answer,
                               'correct_answer': correct_answer, 'correct': correct, 'image': image})
            if task_type == 'quizz':
                correct_answer = None
                for answer, answer_data in data['GamesList'][code]['tasks'][task_id]['answers'].items():
                    if answer_data['correct']:
                        correct_answer = answer
                correct = bool(user_answer == correct_answer)
                user_answer_text = data['GamesList'][code]['tasks'][task_id]['answers'][user_answer]['name']
                correct_answer_text = data['GamesList'][code]['tasks'][task_id]['answers'][correct_answer]['name']
                result.append({'task_type': task_type, 'name': task_data['name'], 'user_answer': user_answer_text,
                               'correct_answer': correct_answer_text, 'correct': correct, 'image': image})
            if task_type == 'checkboxs':
                correct = data['GamesList'][code]['leaderboard'][login]['tasks'][task_id]['cache']
                correct_answers = []
                user_answer_text = []
                user_answer_list = user_answer.split(',')
                for answer_id in user_answer_list:
                    user_answer_text.append(data['GamesList'][code]['tasks'][task_id]['answers'][answer_id]['name'])
                for answer_id, answer_data in data['GamesList'][code]['tasks'][task_id]['answers'].items():
                    if answer_data['correct']:
                        correct_answers.append(answer_data['name'])
                result.append({'task_type': task_type, 'name': task_data['name'], 'user_answer': user_answer_text,
                               'correct_answer': correct_answers, 'correct': correct, 'image': image})
    return result


def collect_stats_and_sort(code):
    data = DataBaseManagement.load_data()
    if code in data['GamesList']:
        if data['GamesList'][code]['complete']:
            GameListener.leaderboard_data.clear()
            for login, user_data in data['GamesList'][code]['leaderboard'].items():
                time = get_game_complete_time(code, login)
                new_entry = {"username": data['Users'][login]['fullname'], "login": login, "score": user_data['score'], "time": time}
                GameListener.leaderboard_data.append(new_entry)
            GameListener.leaderboard_data.sort(key=lambda x: x['score'], reverse=True)


def resize_image(image, target_width, target_height):
    return image.resize((target_width, target_height), resample=Image.Resampling.LANCZOS)


def get_image_dimensions(image):
    width, height = image.size
    if width < height:
        return 'portrait'
    elif width > height:
        return 'landscape'
    else:
        return 'square'
