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
    password = bcrypt.hashpw(password, salt)


    user_repo.create_user(username, email, password)


def create_project(project_repo):
    flag_stop = False

    print()
    print('Введите информацию о проекте!')
    name = input('Название проекта:')
    description = input('Описание проекта:')
    while flag_stop == False:
        try:
            admin_id = int(input('Id администратора:'))
            flag_stop = True
        except ValueError as error:
            print(f'Id состоит только из цифр {error}!')
            print()

    project_repo.create_project(name, description, admin_id)

def assign_task(task_repo, project_repo, user_repo):
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
            flag_stop = True
        except ValueError as error:
            print('Ошибка ввода дэдлайна {error}!')
            print()

    task_repo.create_task(title, description, status, project_id, \
                          assigned_to, deadline)

def menu():
    while True:
        print()
        print('Выберите действие, которое хотите выполнить!')
        print('1 - Создать пользователя')
        print('2 - Создать проект')
        print('3 - Назначить задачу')
        print('4 - Закончить работу')
        try:
            choice = int(input('Введите ваш выбор:'))
            if choice not in (1, 2, 3, 4):
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

    while True:
        choice = menu()
        match choice:
            case 1:
                create_user(user_repo)
            case 2:
                create_project(project_repo)
            case 3:
                assign_task(task_repo, project_repo, user_repo)
            case 4:
                print()
                print('Работа закочена!')
                break

if __name__ == '__main__':
    main()