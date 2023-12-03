import yaml


def load_data():
    try:
        with open('data.yml', 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)
        return data
    except Exception as e:
        print(f'Exception at load_data() {e}')


def save_data(data):
    try:
        with open('data.yml', 'w', encoding='utf-8') as file:
            yaml.dump(data, file)
    except Exception as e:
        print(f'Exception at save_data() {e}')


def check_auth(login, password):
    try:
        data = load_data()
        if data['Users'][login] and data['Users'][login]['password'] == password:
            return True
        else:
            return False
    except Exception as e:
        print(f'Exception at check_auth: {e}')
        return False


def check_login_registered(login):
    try:
        data = load_data()
        if 'users' not in data:
            data['users'] = {}
        if login in data['users']:
            return True
        else:
            return False
    except Exception as e:
        print(f'Exception at check_login_registered(): {e}')
        return True


def check_email_registered(email):
    try:
        data = load_data()
        for login, user_data in data['Users'].items():
            if 'email' in user_data and user_data['email'] == email:
                return True
        return False
    except Exception as e:
        print(f'Exception at check_email_registered(): {e}')
        return True


def get_value_of_user(login, field):
    try:
        data = load_data()
        value = data['Users'][login][f'{field}']
        if value is not None:
            return value
        else:
            return "Error {value not found}"
    except Exception as e:
        print(f'Exception at get_value_of_user(): {e}')
        return "Error {user not found}"


def register_user(fullname, login, password, email, role):
    try:
        data = load_data()
        data['Users'][login] = {
            'fullname': fullname,
            'password': password,
            'email': email,
            'role': role
        }
        save_data(data)
        return True
    except Exception as e:
        print(f'Exception at register_user(): {e}')
        return False
