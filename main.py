import datetime
import bcrypt
from repositories.project_repository import ProjectRepository
from repositories.task_repository import TaskRepository
from repositories.user_repository import UserRepository

def create_user(user_repo):
    print()
    print('Введите информацию о пользователе!')
    username = input('Имя пользователя:')
    email = input('Email пользователя:')
    password = input('Пароль пользователя:')

    # Хэширование пароля
    salt = bcrypt.gensalt()
    password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    user_repo.create_user(username, email, password)

    user_now = user_repo.get_by_username(username)
    return user_now 

def create_project(project_repo, user_now):
    print()
    print('Введите информацию о проекте!')
    name = input('Название проекта:')
    description = input('Описание проекта:')
    admin_id = user_now.get_user_id()
    project_repo.create_project(name, description, admin_id)

def assign_task(task_repo, project_repo, user_repo, user_now):
    flag_stop = False

    print()
    print('Назначте задачу пользователю!')
    title = input('Название задачи:')
    description = input('Описание задачи:')

    while flag_stop == False:
        status = input('Статус задачи (pending, in_progress, completed):')
        if status not in ('pending', 'in_progress', 'completed'):
            print('Неправильно набран стату задачи!')
            print()
        else:
            flag_stop = True

    flag_stop = False
    
    while flag_stop == False:
        try:
            project_id = int(input('Id проекта:'))
            if project_repo.check_project_exists(project_id) is None:
                print()
                print(f'Проекта с {project_id} ID не существует!')
            else:
                flag_stop = True
        except ValueError as error:
            print(f'Ошибка ввода {error}')

    flag_stop = False 

    while flag_stop == False:
        try:
            assigned_to = int(input('Id исполняющего задачу:'))

            if user_repo.check_user_exists(assigned_to) is None:
                print()
                print(f'Пользователя с {assigned_to} ID не существует!')
            else:
                flag_stop = True
        except ValueError as error:
            print(f'Ошибка ввода {error}')

    flag_stop = False

    while flag_stop == False:
        deadline = input('Время дэдлайна:')
        try:
            deadline = datetime.datetime.strptime(deadline, '%Y-%m-%d').date()
            if deadline < datetime.date.today():
                print()
                print('Время дедлайна не может быть меньше нынешнего времени!')
            else:
                flag_stop = True
        except ValueError as error:
            print(f'Ошибка ввода дэдлайна {error}!')
            print()

    task_repo.create_task(title, description, status, project_id, \
                          assigned_to, deadline)

def log_to_system(user_repo):
    user_now = None

    print()
    have_profile= input('У тебя есть профиль? (Y/N): ')
    if have_profile.upper() == 'Y':
        flag_stop = False
        choice = input('Хотите войти в систему по имени пользователя(N) или по email(E)?:')
        while flag_stop == False:
            if choice.upper() == 'E':
                while True:
                    print()
                    email = input('Введите email: ')
                    password = input('Введите пароль: ')

                    if user_repo.check_user_exists_by_email(email) is None:
                        print()
                        print('Данного email нету!')
                    elif user_repo.check_user_correct_password_by_email(email, password) is False:
                        print()
                        print('Неправильно введен пароль!')
                    else:
                        print()
                        print('Вы вошли в систему!')
                        flag_stop = True
                        user_now = user_repo.get_by_email(email)
                        break
            elif choice.upper() == 'N':
                while True:
                    print()
                    name = input('Введите имя пользователя: ')
                    password = input('Ведите пароль: ')
                    
                    if user_repo.check_user_exists_by_username(name) is None:
                        print()
                        print('Данного имени не существует!')
                    elif user_repo.check_user_correct_password_by_username(name, password) is False:
                        print()
                        print('Неправильно введен пароль!')
                    else:
                        print()
                        print('Вы вошли в систему!')
                        flag_stop = True
                        user_now = user_repo.get_by_username(name)
                        break
            else:
                print()
                choice = input('Хотите войти в систему по имени пользователя(N) или по email(E)?:')
    elif have_profile.upper() == 'N':
        user_now = create_user(user_repo)

    return user_now

def menu():
    while True:
        print()
        print('Выберите действие, которое хотите выполнить!')
        print('1 - Создать проект')
        print('2 - Назначить задачу')
        print('3 - Закончить работу')
        try:
            choice = int(input('Введите ваш выбор:'))
            if choice not in (1, 2, 3):
                print()
                print('Такого действия нет!')
            else:
                return choice
        except ValueError as error:
            print(f'Ошибка ввода {error}')

def main():
    user_repo = UserRepository()
    task_repo  = TaskRepository()
    project_repo = ProjectRepository()

    user_now = log_to_system(user_repo)
    if user_now is None:
        print('Работа закончена!')
    else:
        while True:
            choice = menu()
            match choice:
                case 1:
                    create_project(project_repo, user_now)
                case 2:
                    assign_task(task_repo, project_repo, user_repo, user_now)
                case 3:
                    print()
                    print('Работа закочена!')
                    break

if __name__ == '__main__':
    main()